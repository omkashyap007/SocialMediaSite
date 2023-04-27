from django.urls import path
from . import views as private_chat_views

app_name = "chat"

urlpatterns = [
    path("" , private_chat_views.privateChatRoomView , name = "private-chat-room") ,
    path("create-or-return-private-chat" , private_chat_views.createOrReturnPrivateChat , name= "create-or-return-private-chat" ) 
]