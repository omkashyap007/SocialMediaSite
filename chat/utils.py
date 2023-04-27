from chat.models import PrivateChatRoom
from  django.utils import timezone
from datetime import datetime , timedelta
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.serializers.python import Serializer
from .constants import * 
       
def findOrCreatePrivateChat(user1 , user2) :
    try : 
        chat = PrivateChatRoom.objects.get(user1 = user1 , user2 = user2)
    except PrivateChatRoom.DoesNotExist : 
        try : 
            chat = PrivateChatRoom.objects.get(user1 = user2 , user2 = user1)
        except Exception as e : 
            chat = PrivateChatRoom(user1 = user1 , user2 = user2)
            chat.save()
    return chat

def calculateTimeStamp(timestamp) : 
    # today or yesterday
    timestamp = timestamp + timedelta(hours = 5 , minutes = 30) 
    if (naturalday(timestamp)) == "today" or (naturalday(timestamp)) == "yesterday" : 
        str_time = datetime.strftime(timestamp , "%I:%M %p")
        str_time = str_time.strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
        
    else : 
        str_time = datetime.strftime(timestamp , "%d/%m/%Y")
        ts = f"{str_time}"
    return ts

class LazyChatRoomChatMessageEncoder(Serializer) :
    def get_dump_object(self , object):
        dump_object = {
            "msg_type" : MSG_TYPE_MESSAGE  ,
            "msg_id" : str(object.id)  , 
            "user_id" : str(object.user.id) , 
            "username" : str(object.user.username) , 
            "message" : str(object.content) , 
            "profile_image": str(object.user.profile_image.url) , 
            "natural_timestamp" : calculateTimeStamp(object.timestamp) , 
        }
        return dump_object
       