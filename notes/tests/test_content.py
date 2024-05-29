from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Test authorr')
        cls.not_author = User.objects.create_user(username='Not author')
        cls.note = Note.objects.create(
            title='Note 1',
            text='Просто текст.',
            slug='Note_1',
            author=cls.author
        )
        cls.note_by_not_author = Note.objects.create(
            title='Note 2',
            text='Просто текст.',
            slug='Note_2',
            author=cls.not_author
        )
        cls.url = reverse('notes:list')

    def test_notes_list_contains_author_note(self):
        self.client.force_login(self.author)
        response = self.client.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.note_by_not_author, object_list)
        self.assertEqual(len(object_list), 1)


class TestAddPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Test author')
        cls.note = Note.objects.create(
            title='Note 1',
            text='Просто текст.',
            slug='Note_1',
            author=cls.author
        )
        cls.add_note_url = reverse('notes:add')
        cls.add_edit_note_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_add_and_edit_form(self):
        self.client.force_login(self.author)
        urls = (
            self.add_note_url,
            self.add_edit_note_url
        )
        for url in urls:
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
