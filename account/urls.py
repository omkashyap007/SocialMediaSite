from django.urls import path 
from account import views as account_view

app_name = "account"

urlpatterns = [
    path("<int:user_id>/" , account_view.accountView , name ="view") , 
    path("<int:user_id>/edit/" , account_view.editAccountView , name ="edit") , 
    path("<int:user_id>/edit/cropImage/" , account_view.crop_image , name ="crop_image") , 
    
]