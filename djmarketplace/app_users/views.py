from django.shortcuts import redirect
from app_users.models import BuyerStatus, Profile
from django.views.generic import DetailView, CreateView, UpdateView
from app_users.forms import *
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
import logging

logger = logging.getLogger(__name__)


class RegistrationView(CreateView):
    """Класс-вью для регистрации пользователя"""
    model = User
    form_class = RegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save()
        status = BuyerStatus.objects.get(status='starter')
        Profile.objects.create(user=user, status=status)
        login(self.request, user)
        logger.info('User logged in')
        return redirect('index')


class UserLoginView(LoginView):
    """Класс-вью для авторизации пользователя"""
    template_name = 'users/login.html'

    def get_success_url(self):
        logger.info('User logged in')
        return super().get_success_url()


class UserDetailView(DetailView):
    """Класс-вью личный кабинет пользователя"""
    template_name = 'users/account.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return User.objects.select_related('profile').get(pk=pk)


class FillUpWalletView(UpdateView):
    """Класс-вью для пополнения кошелька"""
    model = Profile
    template_name = 'users/fill_up_wallet.html'
    success_url = 'account'
    form_class = FillUpWalletForm
    initial = {}

    def get_initial(self):
        self.initial.update({'balance': self.request.user.profile.balance})
        return super(FillUpWalletView, self).get_initial()

    def form_valid(self, form):
        profile = form.save(commit=False)
        balance = self.initial.get('balance')
        profile.change_balance(balance)
        return redirect(reverse_lazy(self.success_url, kwargs={'pk': self.request.user.pk}))

