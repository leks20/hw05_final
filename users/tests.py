from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core import mail

User = get_user_model()


class SignUpTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test',
            email='test@mail.ru',
            password='test123'
        )

    def test_mail(self):
        mail.send_mail(
            'Регистрация',
            'Вы успешно прошли регистрацию на сайте',
            'from@example.com',
            ['test@mail.ru'],
            fail_silently=False,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Регистрация')

    def test_profile(self):
        # self.client.login(username='test', password='test123')
        response = self.client.get('/test/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['profile'], User)
        self.assertEqual(
            response.context['profile'].username,
            self.user.username
        )
