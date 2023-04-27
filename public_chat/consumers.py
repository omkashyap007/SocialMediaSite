import json
from django.utils import timezone
from datetime import datetime , timedelta
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.humanize.templatetags.humanize import naturalday
from public_chat.models import PublicChatRoom , PublicRoomChatMessage
from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize
from .constants import *
from chat.exceptions import ClientError
from chat.utils import calculateTimeStamp 

User = get_user_model()

class PublicChatConsumer(AsyncJsonWebsocketConsumer): 
    
    async def connect(self) :
        await self.accept()
        self.room_id = None
        
    async def disconnect(self , code):
        try :
            if self.room_id != None : 
                await self.leave_room(self.room_id)
        except Exception as e :
            self.handle_client_error(e)
        
        
    async def receive_json(self, content):
        command = content.get("command" , None)
        try :
            if command == "send" : 
                if len(content["message"].strip().lstrip().rstrip()) == 0: 
                    raise ClientError(422 , "You can't send an empty message !")
                await self.send_room(
                    content["room_id"] ,
                    {"message":content["message"]} 
                )
            elif command == "join" :
                await self.join_room(content["room_id"])
            elif command == "leave" : 
                await self.leave_room(content["room_id"])
            elif command == "get_room_chat_messages" :
                await self.display_progress_bar(True)
                room = await get_room_or_error(content["room_id"])
                payload  = await get_room_chat_messages(room , content["page_number"])
                if payload != None :
                    payload = json.loads(payload)
                    await self.send_messages_payload(payload["messages"] , payload["new_page_number"])
                else : 
                    raise ClientError(204 , "Something went wrong retrieving chatroom messages .")
                await self.display_progress_bar(False)
        except ClientError as e : 
            await self.display_progress_bar(False)
            await self.handle_client_error(e)
            
    async def send_room(self , room_id ,  content) : 
        try : 
            if self.room_id != None :
                if str(room_id) != str(self.room_id):
                    raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
                if not is_authenticated(self.scope["user"]) : 
                    raise ClientError("AUTH_ERROR" ,"You must be authenticated to chat !")
            else : 
                raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
            room = await get_room_or_error(room_id)
            user = self.scope["user"]
            chat_message = await create_public_room_chat_message(room, user, content["message"])
            await self.channel_layer.group_send(
                room.group_name , 
                {                 
                    "type" : "chat_message" , 
                    "profile_image" : user.profile_image.url , 
                    "username" : user.username , 
                    "user_id" : user.id , 
                    "message" : content["message"] , 
                    "msg_id" : chat_message.id 
                }
            )
        except ClientError as e  : 
            await self.handle_client_error(e) 
        
    async def chat_message(self,  event) :
        
        timestamp = calculateTimeStamp(timezone.now())
        await self.send_json(
            {   
                "msg_type" : MSG_TYPE_MESSAGE , 
                "message" : event["message"] , 
                "username" : event["username"] , 
                "profile_image" : event["profile_image"] , 
                "user_id" : event["user_id"] , 
                "natural_timestamp" : timestamp ,
                "msg_id" : event["msg_id"] 
            }
        )
        

    async def join_room(self , room_id) :
        is_auth = is_authenticated(self.scope["user"])
        try  :
            room = await get_room_or_error(room_id)
        except ClientError as e : 
            await self.handle_client_error(e)
        
        if is_auth : 
            await connect_user(room , self.scope["user"])
        # store the room id that we are in the room .
        # consumers can store data in them as variables , but you need to create an empty var before storing any var . 
        self.room_id = room.id
        
        await self.channel_layer.group_add(
            room.group_name , 
            self.channel_name 
        )
        
        # tell the client to finish opening the room
        await self.send_json(
            {
                "join" : str(room.id) ,
                "username" : self.scope["user"].username , 
            }
        )
        
        await self.send_connected_users_count_to_group(room_id)
    
    async def leave_room(self, room_id) : 
        """
        Called when someone leaves the room .         
        """
        is_auth = is_authenticated(self.scope["user"])
        try : 
            room = await get_room_or_error(room_id)
        except ClientError as e : 
            await self.handle_client_error(e)
            
        if is_auth : 
            await disconnect_user(room , self.scope["user"])
            
        self.room_id = None
        
        await self.channel_layer.group_discard(
            room.group_name , 
            self.channel_name 
        )
        await self.send_connected_users_count_to_group(room_id)
        
    async def send_messages_payload(self , messages , new_page_number) :
        """
        Sends a payload of messages to the ui
        """
        await self.send_json({
            "messages_payload" : "messages_payload" , 
            "messages" : messages , 
            "new_page_number" : new_page_number , 
        })
            
    async def handle_client_error(self , e) : 
        """
        Called by the client error 
        """
        errorData = {}
        errorData["error"] = e.code
        if e.message :
            errorData["message"] = e.message
            await self.send_json(errorData)
        return
        
    async def display_progress_bar(self , is_displayed) : 
        """
            1. is_display = True
            display the progress bar to ui
            
            2. is_display  = False
            hide the progress bar to ui 
        """    
        await self.send_json(
            {
                "display_progress_bar" : is_displayed
            }
        )
    async def send_connected_users_count_to_group(self , room_id) : 
        try : 
            room = await get_room_or_error(room_id)
            users_count = await get_num_connected_users(room)
            await self.channel_layer.group_send(
                room.group_name , 
                {
                "type" : "send_count",
                "get_user_count" : "get_user_count" , 
                "users_count" : users_count , }
                )
        except ClientError as e : 
            await self.handle_client_error(e)
        
    async def send_count(self, content):
        await self.send_json(
            {
                
                "msg_type" : MSG_TYPE_GET_CONNECTED_USERS_COUNT , 
                "users_count" : content["users_count"]  ,
            }
        )
    
@database_sync_to_async
def get_num_connected_users(room) : 
    if room.users : 
        return len(room.users.all())
    return 0
    
def is_authenticated(user):
    if user.is_authenticated : 
        return True
    return  False

# the queries for adding and removing the users is totally synchronous , you need to make it sync .
# so using database_async_to_sync decorator will do the work to make this thing work with 
# the consumers

@database_sync_to_async
def create_public_room_chat_message(room , user , message) :
    return PublicRoomChatMessage.objects.create(user = user , room = room , content = message)

@database_sync_to_async
def connect_user(room , user) :
    return room.connect_user(user)

@database_sync_to_async
def check_user_in_room(room , user) : 
    return user in room.users.all()

@database_sync_to_async
def disconnect_user(room , user): 
    return room.disconnect_user(user)

@database_sync_to_async
def get_room_or_error(room_id) : 
    """
    Tries to fetch teh room for the suer 
    """
    try : 
        room = PublicChatRoom.objects.get(id = room_id)
    except PublicChatRoom.DoesNotExist : 
        raise ClientError("ROOM_INVALID" , "Invalid Room")
    return room
        

@database_sync_to_async
def get_room_chat_messages(room , page_number) : 
    try : 
        qs = PublicRoomChatMessage.objects.by_room(room)
        p = Paginator(object_list = qs , per_page = DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)
        
        # a = p.page(page_number)
        # print(a.object_list)
        payload = {}
        new_page_number = int(page_number)
        if new_page_number <= p.num_pages :
            new_page_number +=1
            s = LazyRoomChatMessageEncoder()
            data = s.serialize(p.page(page_number).object_list)
            # print(data)
            # print(type(data))
            payload["messages"] = data
        else : 
            payload["messages"] = "None"
        payload["new_page_number"] = new_page_number
        return json.dumps(payload)
    except Exception as e : 
        print("Exception : " + str(e))
        return None
        
class LazyRoomChatMessageEncoder(Serializer) : 
    def get_dump_object(self , object) :
        dump_object = {}
        dump_object["msg_type"] = MSG_TYPE_MESSAGE
        dump_object["user_id"] = object.user.id
        dump_object["username"] = object.user.username
        dump_object["message"] = object.content
        dump_object["profile_image"] = object.user.profile_image.url
        dump_object["natural_timestamp"] = calculateTimeStamp(object.timestamp)
        dump_object["msg_id"] = object.id
        return dump_object
