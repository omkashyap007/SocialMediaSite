import json
from itertools import chain
from django.shortcuts import render
from django.conf import settings
from chat.models import PrivateChatRoom , RoomChatMessage
from chat.utils import findOrCreatePrivateChat
from django.conf import settings 
from django.http import HttpResponse
from account.models import Account
DEBUG = True


def privateChatRoomView(request , *args , **kwargs):
    context = {}    
    context["debug"] = DEBUG
    context["debug_mode"] = settings.DEBUG
    user = request.user
    room_id = kwargs.get("room_id") or request.GET.get("room_id")  
    print(room_id)
    if not user.is_authenticated : 
        return redirect("login") 

    if room_id : 
        try :
            room = PrivateChatRoom.objects.get(id = room_id) 
            context["room"] = room
        except : 
            pass
    #1. find all room this user is part of 
    
    rooms1 = PrivateChatRoom.objects.filter(user1 = user , is_active = True)
    rooms2 = PrivateChatRoom.objects.filter(user2 = user , is_active = True)
    rooms = list(chain(rooms1 , rooms2))
    
    message_and_friend = []
    for room in rooms : 
        if room.user1 == user : 
            friend = room.user2
        else : 
            friend = room.user1
        message_and_friend.append(
            {
                "message" : "" , 
                "friend" : friend
            }
        )
    context["m_and_f"] = message_and_friend
    return render(request , "chat/room.html" , context)

def createOrReturnPrivateChat(request , *args , **kwargs) : 
    user1 = request.user
    payload = {}
    if user1.is_authenticated : 
        if request.method == "POST" : 
            user2_id = request.POST.get("user2_id")
            try  :
                user2 = Account.objects.get(id = user2_id) 
                chat = findOrCreatePrivateChat(user1, user2)
                payload["response"] = "Successfully got the chat ..."
                payload["chatroom_id"] = chat.id
            except :
                payload["response"] = "Unable to start the chat wtih the user !"
    else : 
        payload["response"] = "You can't start chat until you are authenticated !"
    return HttpResponse(json.dumps(payload) , content_type = "application/json")    

