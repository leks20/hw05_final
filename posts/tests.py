from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.core.cache.backends import locmem
from django.core.cache import cache
from posts.models import Post, Group

User = get_user_model()

TEST_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


@override_settings(CACHES=TEST_CACHE)
class PostsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='proverkin',
            email='proverkin@mail.ru',
            password='proverkin123'
        )
        self.client.login(username='proverkin', password='proverkin123')

    def test_logged_in(self):
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get('/new/')

        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post(self):

        response = self.client.post(
            '/new/',
            {'text': "Проверочный текст"},
            follow=True)

        self.assertRedirects(response, '/')

        for url in ('', '/proverkin/', '/proverkin/1/'):
            response = self.client.get(url)
            self.assertContains(response, "Проверочный текст")

    def test_edit_post(self):
        self.client.post('/new/', {'text': "Проверочный текст"}, follow=True)
        response = self.client.post(
            '/proverkin/1/edit/',
            {'text': "Отредактированный текст"},
            follow=True)

        self.assertRedirects(response, '/proverkin/1/')

        for url in ('', '/proverkin/', '/proverkin/1/'):
            response = self.client.get(url)
            self.assertContains(response, "Отредактированный текст")

    def test_comment(self):
        Post.objects.create(
            author=self.user,
            text="Текст")

        self.client.post('/proverkin/1/comment/', {
            'text': "Проверочный комментарий",
            }, follow=True)

        response = self.client.get('/proverkin/1/')
        self.assertContains(response, 'Проверочный комментарий')

        self.client.logout()

        self.client.post('/proverkin/1/comment/', {
                'text': "Проверочный комментарий 2"
                }, follow=True)

        response = self.client.get('/proverkin/1/')
        self.assertNotContains(response, 'Проверочный комментарий 2')


class ErrorTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='proverkin',
            email='iv.proverkin@mail.ru',
            password='123dis456'
        )

    def test_page_not_found(self):
        self.user.delete()
        response = self.client.get('/proverkin/')
        self.assertEqual(response.status_code, 404)


class MediaTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='proverkin',
            email='iv.proverkin@mail.ru',
            password='123dis456'
        )
        self.client.login(username='proverkin', password='123dis456')
        self.group = Group.objects.create(
            title="test",
            slug='test',
        )

    def test_post_has_img(self):
        with open('media/posts/123.jpeg', 'rb') as fp:
            self.client.post('/new/', {
                    'text': "Проверочный пост",
                    'image': fp,
                    'group': 1
                    }, follow=True)

        for url in ('', '/proverkin/', '/proverkin/1/', '/group/test/'):
            response = self.client.get(url)
        self.assertContains(response, '<img')

    def test_not_graphic_format(self):
        with open('requirements.txt', 'rb') as fp:
            response = self.client.post('/new/', {
                    'text': "Testing",
                    'image': fp
                    }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'image', [
            'Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.'])


class CacheTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='proverkin',
            email='proverkin@mail.ru',
            password='123dis456'
        )
        self.client.login(username='proverkin', password='123dis456')

    def test_cache(self):

        response = self.client.post('/new/', {
            'text': "Проверка"}, follow=True)
        self.assertRedirects(response, '/')

        # проверка, что OrderedDict() содержит кеш
        self.assertTrue(locmem._caches[""])
        cache.clear()
        # проверка, что OrderedDict() пустой
        self.assertFalse(locmem._caches[""])


@override_settings(CACHES=TEST_CACHE)
class FollowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='proverkin',
            email='proverkin@mail.ru',
            password='123dis456')
        self.test = User.objects.create_user(
            username='test',
            email='test@mail.ru',
            password='test123')
        self.test2 = User.objects.create_user(
            username='test2',
            email='test2@mail.ru',
            password='test456')

    def test_follow(self):

        self.client.login(username='proverkin', password='123dis456')

        response = self.client.get('/test/follow/', follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/test/unfollow/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_follow_post(self):

        self.client.login(username='proverkin', password='123dis456')
        post = Post.objects.create(
            author=self.user,
            text="Какой-то пост")
        self.client.logout()

        self.client.login(username='test', password='test123')
        response = self.client.get('/proverkin/follow/', follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/follow/')
        self.assertContains(response, post.text)
        self.client.logout()

        self.client.login(username='test2', password='test456')
        response = self.client.get('/follow/')
        self.assertNotContains(response, post.text)
