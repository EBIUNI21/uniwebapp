from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from petpals.forms import PageForm
from petpals.models import Category, Page, Post, Comment, UserProfile, Like, user_path
from petpals.templatetags import petweb_template_tags


class CategoryModelTests(TestCase):
    def test_slug_is_created(self):
        category = Category.objects.create(name="Test Category")
        self.assertEqual(category.slug, "test-category")

    def test_string_representation(self):
        category = Category.objects.create(name="Python")
        self.assertEqual(str(category), "Python")

    def test_meta_verbose_name_plural(self):
        self.assertEqual(str(Category._meta.verbose_name_plural), "categories")

class PageModelTests(TestCase):
    def test_page_creation_and_str(self):
        cat = Category.objects.create(name="WebDev")
        page = Page.objects.create(category=cat, title="Django", url="https://www.djangoproject.com", views=10)
        self.assertEqual(str(page), "Django")
        self.assertEqual(page.views, 10)

class UserProfileModelTests(TestCase):
    def test_profile_str_and_defaults(self):
        user = User.objects.create_user(username="john", password="testpass")
        profile = UserProfile.objects.create(user=user)
        self.assertEqual(str(profile), "john")
        self.assertTrue(profile.picture.name.endswith("default.png"))

class PostModelTests(TestCase):
    def test_post_creation(self):
        user = User.objects.create_user(username="amy", password="pass")
        post = Post.objects.create(user=user, title="Hello", statement="Hello world!")
        self.assertEqual(str(post), "Hello")
        self.assertEqual(post.views, 0)

    def test_post_likes(self):
        user = User.objects.create_user(username="likeguy", password="123")
        post = Post.objects.create(user=user, title="Like Test")
        post.likes.add(user, through_defaults={})
        self.assertIn(user, post.likes.all())

class CommentModelTests(TestCase):
    def test_comment_and_reply(self):
        user = User.objects.create_user(username="commenter", password="pass")
        post = Post.objects.create(user=user, title="New Post")
        comment = Comment.objects.create(user=user, post=post, content="First!")
        reply = Comment.objects.create(user=user, post=post, content="Replying", replyee=comment)
        self.assertEqual(str(comment), "First!")
        self.assertIn(reply, comment.get_replies())

class LikeModelTests(TestCase):
    def test_like_str(self):
        user = User.objects.create_user(username="liker", password="pass")
        post = Post.objects.create(user=user, title="Great Post")
        like = Like.objects.create(user=user, post=post)
        self.assertEqual(str(like), "liker liked Great Post")




class UserPathHelperFunctionTests(TestCase):
    def test_user_path_returns_correct_format(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        class MockInstance:
            def __init__(self, user):
                self.user = user

        instance = MockInstance(user=user)
        path = user_path(instance, "myphoto.png")
        
        expected_path = f"user_{user.id}/myphoto.png"
        self.assertEqual(path, expected_path)





class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(title='Test Post', statement='Test content', user=self.user)
        self.client.login(username='testuser', password='testpass')

    def test_index_view(self):
        response = self.client.get(reverse('petpals:index'))
        self.assertEqual(response.status_code, 200)

    def test_about_view(self):
        session = self.client.session
        session['last_visit'] = '2000-01-01 00:00:00.000000'
        session.save()
        response = self.client.get(reverse('petpals:about'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('visits', response.context)

    def test_show_category_view(self):
        response = self.client.get(reverse('petpals:show_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)

  

    def test_create_post_view_post(self):
        response = self.client.post(reverse('petpals:create_post'), {
            'title': 'Created Post',
            'statement': 'Some statement'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='Created Post').exists())

    def test_account_view_post(self):
        response = self.client.post(reverse('petpals:account'), {
            'bio': 'Updated bio'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_edit_profile_post(self):
        response = self.client.post(reverse('petpals:edit_profile'), {
            'bio': 'Edited bio'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_delete_post(self):
        response = self.client.post(reverse('petpals:delete_post', args=[self.post.id]))
        self.assertRedirects(response, reverse('petpals:account'))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_view_post_add_comment(self):
        response = self.client.post(reverse('petpals:view_post', args=[self.post.id]), {
            'content': 'Test comment'
        })
        self.assertRedirects(response, reverse('petpals:view_post', args=[self.post.id]))
        self.assertTrue(Comment.objects.filter(post=self.post).exists())

    def test_like_post_ajax(self):
        response = self.client.post(reverse('petpals:like_post'), {'post_id': self.post.id})
        self.assertEqual(response.status_code, 200)


    def test_add_category_post_valid(self):
        response = self.client.post(reverse('petpals:add_category'), {
            'name': 'Test Category 2',
            'views': 0,
            'likes': 0,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Test Category 2').exists())

    def test_add_category_invalid_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('petpals:add_category'), {'name': ''}) 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_add_page_post_invalid(self):
        data = {
            'title': '', 
            'url': 'not-a-url',
        }
        response = self.client.post(reverse('petpals:add_page', kwargs={'category_name_slug': self.category.slug}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petpals/add_page.html')
        self.assertContains(response, 'form')  
    def test_add_page_redirects_if_category_missing(self):
        response = self.client.get(reverse('petpals:add_page', kwargs={'category_name_slug': 'missing'}))
        self.assertRedirects(response, '/petpals/')

    def test_add_page_get(self):
        response = self.client.get(reverse('petpals:add_page', kwargs={'category_name_slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petpals/add_page.html')

    def test_restricted_view_authenticated(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('petpals:restricted'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'petpals/restricted.html')




class PageFormCleanDirectTest(TestCase):
    def test_clean_adds_http_prefix_directly(self):
        form = PageForm()
        form.cleaned_data = {
            'title': 'Test Page',
            'url': 'example.com',
            'views': 0
        }
        cleaned = form.clean()
        self.assertEqual(cleaned['url'], 'http://example.com')



class TemplateTagTests(TestCase):
    def test_get_category_list_returns_context(self):
        cat1 = Category.objects.create(name="Dogs")
        cat2 = Category.objects.create(name="Cats")

        context = petweb_template_tags.get_category_list(current_category="Dogs")

        self.assertIn('categories', context)
        self.assertIn(cat1, context['categories'])
        self.assertIn(cat2, context['categories'])
        self.assertEqual(context['current_category'], "Dogs")



class RegisterViewTests(TestCase):
    @patch('petpals.views.render')
    def test_register_get(self, mock_render):
        mock_render.return_value = HttpResponse("OK")  
        response = self.client.get(reverse('petpals:register'))
        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()



    @patch('petpals.views.render')
    def test_register_invalid_post(self, mock_render):
        mock_render.return_value = HttpResponse("OK")
        response = self.client.post(reverse('petpals:register'), {
            'username': '',  
            'password': '123',
        })
        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()

    def test_register_valid_post(self):
        response = self.client.post(reverse('petpals:register'), {
            'username': 'newuser',
            'password': 'securepass123',
        })
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(User.objects.filter(username='newuser').exists())

