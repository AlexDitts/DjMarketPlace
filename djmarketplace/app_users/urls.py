from django.urls import path
from app_users.views import *


urlpatterns = [
    path('registration', RegistrationView.as_view(), name='registration'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(next_page='index'), name='logout'),
    path('account/<int:pk>', UserDetailView.as_view(), name='account'),
    path('fill_up_wallet/<int:pk>', FillUpWalletView.as_view(), name='fill_up_wallet')
]
