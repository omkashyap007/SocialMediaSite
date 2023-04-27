from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from account import views as account_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("personal.urls")),
    path("account/", include("account.urls" , namespace = "account")),
    
    path("friend/" , include("friend.urls" , namespace = "friend")) , 
    
    path("register/" , account_view.registerUser , name = "register-user") , 
    path("login/" , account_view.loginUser , name = "login-user" ) , 
    path("logout/" , account_view.logoutUser , name = "logout-user") ,
    path("search/" , account_view.account_search_view , name ="search") , 

    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='password_reset/password_change_done.html'
         ),
         name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_reset/password_change.html'),
         name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # private chat urls
    path("chat/" , include("chat.urls" , namespace = "chat")) , 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
