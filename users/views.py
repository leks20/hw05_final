from django.views.generic import CreateView
from django.core.mail import send_mail

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login/"
    template_name = "signup.html"

    def form_valid(self, form):
        email = form.cleaned_data['email']
        self.send_mail_ls(email)
        return super().form_valid(form)

    def send_mail_ls(self, email):
        send_mail('Регистрация', 'Вы успешно прошли регистрацию на сайте!', 'yatube.ru <admin@yatube.ru>', [email], fail_silently=False)

