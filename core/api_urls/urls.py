from django.urls import path
from core.api import *

urlpatterns = [
#--------------------------------------------------------------------------------------------------#
# Autenticación
#--------------------------------------------------------------------------------------------------#
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('resend/verification/code/', ResendVerificationCodeAPIView.as_view(), name='resend-verification-code'),
    path('email/verification/', EmailVerificationAPIView.as_view(), name='email-verification'), 
    path('recover/account/', RecoverAccountAPIView.as_view(), name='recover-account'), 
    path('recover/account/verification/', RecoverAccountVerificationAPIView.as_view(), name='recover-account-verification'),   
    path('recover/account/change/password/', RecoverAccountChangePasswordAPIView.as_view(), name='recover-account-change-password'),   

#--------------------------------------------------------------------------------------------------#
# Usuarios
#--------------------------------------------------------------------------------------------------#
    path('user/', UserIndexAPIView.as_view(), name='user-index'),
    path('user/update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('user/show/', UserShowAPIView.as_view(), name='user-show'),
    path('user/change/password/', UserChangePasswordAPIView.as_view(), name='user-change-password'),
]