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
    path('user/<int:pk>/', UserShowAPIView.as_view(), name='user-show'),
    
#--------------------------------------------------------------------------------------------------#
# Usuario-Perfil
#--------------------------------------------------------------------------------------------------#
    path('user/change/password/', UserChangePasswordAPIView.as_view(), name='user-change-password'),
    path('user/upload/photo/', UserUploadPhotoAPIView.as_view(), name='user-upload-photo'),
    
#--------------------------------------------------------------------------------------------------#
# Usuario-Seguimiento
#--------------------------------------------------------------------------------------------------#
    path('follow/', FollowUserIndexCreateAPIView.as_view(), name='follow-user'),
    path('follow/<int:pk>/', FollowUserDetailAPIView.as_view(), name='follow-detail'),

#--------------------------------------------------------------------------------------------------#
# Paises
#--------------------------------------------------------------------------------------------------#
    path('country/', CountryIndexAPIView.as_view(), name='country-index'),
    path('country/<int:pk>/', CountryShowAPIView.as_view(), name='country-show'),

#--------------------------------------------------------------------------------------------------#
# Estados
#--------------------------------------------------------------------------------------------------#
    path('status/', StatusIndexAPIView.as_view(), name='status-index'),
    path('status/<int:pk>/', StatusShowAPIView.as_view(), name='status-show'),

#--------------------------------------------------------------------------------------------------#
# Tipos de publicación
#--------------------------------------------------------------------------------------------------#
    path('type-post/', TypePostIndexAPIView.as_view(), name='type-post-index'),
    path('type-post/<int:pk>/', TypePostShowAPIView.as_view(), name='type-post-show'),
    
#--------------------------------------------------------------------------------------------------#
# Reacciones
#--------------------------------------------------------------------------------------------------#
    path('reaction/', ReactionIndexCreateAPIView.as_view(), name='reaction'),
    path('reaction/<int:pk>/', ReactionDetailAPIView.as_view(), name='reaction-detail'),
    
#--------------------------------------------------------------------------------------------------#
# Reportes
#--------------------------------------------------------------------------------------------------#
    path('report/', ReportIndexCreateAPIView.as_view(), name='report'),
    path('report/<int:pk>/', ReportShowAPIView.as_view(), name='report-show'),
    
#--------------------------------------------------------------------------------------------------#
# Publicaciones
#--------------------------------------------------------------------------------------------------#
    path('post/', PostIndexCreateAPIView.as_view(), name='post'),
    path('post/<int:pk>/', PostDetailAPIView.as_view(), name='post-detail'),
    
#--------------------------------------------------------------------------------------------------#
# Compartir
#--------------------------------------------------------------------------------------------------#
    path('share/', ShareIndexCreateAPIView.as_view(), name='share'),
    path('share/<int:pk>/', ShareDetailAPIView.as_view(), name='share-detail'),
    
#--------------------------------------------------------------------------------------------------#
# Comentarios
#--------------------------------------------------------------------------------------------------#
    path('comment/', CommentIndexCreateAPIView.as_view(), name='comment'),
    path('comment/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
    

]