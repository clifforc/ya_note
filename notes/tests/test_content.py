from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Test author')
        user_notes = [
            Note(
                title=f'Note {index}',
                text='Просто текст.',
                slug=f'Note_{index}',
                author=cls.author
            )
            for index in range(10)
        ]
        Note.objects.bulk_create(user_notes)

    def test_notes_order(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        all_ids = [note.id for note in object_list]
        sorted_notes = sorted(all_ids)
        self.assertEqual(all_ids, sorted_notes)


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
