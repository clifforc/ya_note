from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()
URL_SUCCESS = reverse('notes:success')


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'note title'
    NOTE_TEXT = 'note text'
    NOTE_SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Test author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes_count = Note.objects.count()
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
            'author': cls.author_client
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_user_cant_use_same_slug(self):
        Note.objects.create(
            title='new note',
            text='new text',
            slug=self.NOTE_SLUG,
            author=self.author
        )
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.NOTE_SLUG}{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        self.assertRedirects(response, URL_SUCCESS)
        self.assertEqual(Note.objects.count(), self.notes_count + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'note title'
    NOTE_TEXT = 'note text'
    NOTE_SLUG = 'note_slug'

    NEW_NOTE_TITLE = 'new note title'
    NEW_NOTE_TEXT = 'new note text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Test author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Test reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.notes_count = Note.objects.count()
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
            'author': cls.author_client
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, URL_SUCCESS)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count + 1)
