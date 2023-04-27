from django.urls import path 
from friend import views as friend_view

app_name = "friend" 
urlpatterns = [
    path("friend_request/" , friend_view.send_friend_request , name = "friend-request") ,
    path("friend_request/<int:user_id>/"  , friend_view.friend_requests , name = "friend-requests") , 
     path('friend_request_accept/<friend_request_id>/', friend_view.accept_friend_request, name='friend-request-accept'),
    path("friend_remove/", friend_view.remove_friend , name = "remove-friend") ,  
    
    path('friend_request_decline/<int:friend_request_id>/', friend_view.decline_friend_request, name='friend-request-decline'),
    
    path("friend_request_cancel/<int:friend_request_id>" , friend_view.cancel_friend_request , name = "friend-request-cancel") ,
    
    path("list/<user_id>/" , friend_view.friend_list_view , name = "friend-list") , 
]