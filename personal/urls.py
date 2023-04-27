from django.urls import path 
from personal import views as personal_views

urlpatterns = [
    path("" , personal_views.HomeScreenView , name = "home") , 
]