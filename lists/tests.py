from django.test import TestCase

# Create your tests here.

from django.core.urlresolvers import resolve
from lists.views import home_page
from lists.models import Item, List
from django.http import HttpRequest
from django.template.loader import render_to_string


class ListAndItemModelTest(TestCase):

    def test_saving_items(self):
        list_ = List()
        list_.save()

        first = Item()
        first.text = "This is the first"
        first.list = list_
        first.save()

        second = Item()
        second.text = "A second text example"
        second.list = list_
        second.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)
        saved = Item.objects.all()
        self.assertEqual(saved.count(), 2)
        self.assertEqual(saved[0].text, "This is the first")
        self.assertEqual(saved[1].text, "A second text example")
        self.assertEqual(saved[0].list, list_)
        self.assertEqual(saved[1].list, list_)


class ListViewTest(TestCase):

    def test_passes_correct_list(self):
        correct = List.objects.create()
        response = self.client.get('/lists/%d/' % (correct.id,))
        self.assertEqual(response.context['list'], correct)

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertTemplateUsed(response, 'list.html')

    def test_display_muliple_todo_for_correct_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text="item1", list=correct_list)
        Item.objects.create(text="item2", list=correct_list)

        incorrect_list = List.objects.create()
        Item.objects.create(text=" not item1", list=incorrect_list)
        Item.objects.create(text=" not item2", list=incorrect_list)

        response = self.client.get('/lists/%d/' % (correct_list.id,))

        self.assertContains(response, "item1")
        self.assertContains(response, "item2")

        self.assertNotContains(response, "not item1")
        self.assertNotContains(response, "not item2")

class HomePageTest(TestCase):

    def test_if_home_page_resolved(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_correct(self):
        request = HttpRequest()
        response = home_page(request)
        expected = render_to_string('home.html')
        self.assertEqual(response.content.decode(), expected)


class NewListTest(TestCase):

    def test_home_page_post_request(self):
        self.client.post('/lists/new',
                         data={'item_text': "A new to do row"})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new to do row")

    def test_home_page_redirect(self):
        response = self.client.post(
            '/lists/new',
            data={'item_text': 'A new list item'}
        )
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/%d/' % (new_list.id,))


class NewItemTest(TestCase):

    def test_save_post_to_existing_list(self):
        correct = List.objects.create()

        self.client.post('/lists/%d/add_item' % (correct.id,),
                         data={'item_text': 'list item in correct list'})
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Item.objects.first().text, "list item in correct list")

    def test_redirect_to_list_view(self):
        correct = List.objects.create()

        response = self.client.post('/lists/%d/add_item' % (correct.id,),
                            data={'item_text': 'list item'})

        self.assertRedirects(response, '/lists/%d/' % (correct.id,))
