from django.views.generic import CreateView
from django.core.mail import send_mail

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login/"
    template_name = "signup.html"

    send_mail(
        'Регистрация',
        'Вы успешно прошли регистрацию на сайте',
        'from@example.com',  # Это поле От:
        ['to@example.com'],  # Это поле Кому:
        fail_silently=False,
    )

    # def form_valid(self, form):
    #     email = form.cleaned_data['email']
    #     send_mail_ls(email)
    #     return super().form_valid(form)

    # def send_mail_ls(email):
    #     send_mail('Подтверждение регистрации Yatube', 'Вы зарегистрированы!', 'Yatube.ru <admin@yatube.ru>',[email], fail_silently=False)
