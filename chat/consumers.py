import json
from django.utils import timezone
from chat.utils import calculateTimeStamp
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from chat.utils import findOrCreatePrivateChat
from friend.models import FriendList
from account.utils import LazyAccountEncoder
from chat.models import PrivateChatRoom , RoomChatMessage , UnreadChatRoomMessages
from .exceptions import ClientError
from .constants import *
from chat.utils import LazyChatRoomChatMessageEncoder
from django.core.paginator import Paginator
from account.models import Account
import asyncio


class ChatConsumer(AsyncJsonWebsocketConsumer) :
    async def connect(self):
        await self.accept()
        self.room_id = None
        
    async def receive_json(self , content):
        command = content.get("command" , None)
        try : 
            if command == "join" :
                room_id = int(content["room_id"])
                await self.join_room(room_id)
                self.room_id = room_id
            if command == "leave" : 
                self.leave_room(content["room_id"])
            if command == "send" : 
                if len(content["message"].strip().rstrip().lstrip()) != 0 : 
                    await self.send_room(content["room_id"] , content["message"])
                else : 
                    raise ClientError(422 , "Cannot send empty message")
            if command == "get_room_chat_messages" :
                await self.display_progress_bar(True)
                room = await get_room_or_error(content["room_id"], self.scope["user"])
                payload = await get_room_chat_messages(room, content["page_number"])
                
                if payload != None : 
                    payload = json.loads(payload)
                    await self.send_messages_payload(payload["messages"] , payload["new_page_number"])
                else :
                    raise ClientError(204, "Something went wrong while retrieving the chat room messages !")
                await self.display_progress_bar(False)
            if command == "get_user_info" :
                await self.display_progress_bar(True)
                room = await get_room_or_error(content["room_id"], self.scope["user"])
                payload = await get_user_info(room , self.scope["user"])
                if payload != None : 
                    await self.send_user_info_payload(payload)
                else : 
                    raise ClientError("INVALID PAYLOAD" ,"Something went wrong retrieving the other users account detail !")  
                await self.display_progress_bar(False)
        except ClientError as e:
            await self.display_progress_bar(False)
            await self.handle_client_error(e)
    async def disconnect(self , close_code) :
        try : 
            if self.room_id != None : 
                await self.leave_room(self.room_id)
        except ClientError as e : 
            self.handle_client_error(e)
            
    # async def leave_room(self , room_id) : 
    #     room = await self.get_room_or_error(room_id)
    #     await disconnect_user(room, self.scope["user"])
    #     try : 
    #         await self.channel_layer.group_discard(
    #             room.group_name , 
    #             self.channel_name
    #         )
    #     except ClientError as e : 
    #         return self.handle_client_error(e)
    
    async def chat_join(self , event) : 
        if event["username"] : 
            await self.send_json({
                "msg_type" : MSG_TYPE_ENTER , 
                "room" :  event["room_id"] , 
                "profile_image" : event["profile_image"] , 
                "username" : event["username"] , 
                "user_id" : event["user_id"] , 
                "message" : event["username"] + " connected." , 
            })        
    
    async def join_room(self,  room_id ) :
        try : 
            room = await get_room_or_error(room_id , self.scope["user"])
        except ClientError as e : 
            await self.handle_client_error(e)
            
        await connect_user(room, self.scope["user"])
        
        self.room_id = room_id
        
        await on_user_connected(room ,self.scope["user"])
        
        await self.channel_layer.group_add(
            room.group_name , 
            self.channel_name
        )
            
        await self.send_json({
            "join" :str(room.id), 
        })
        
        if self.scope["user"].is_authenticated : 
            await self.channel_layer.group_send(
                room.group_name , 
                {
                    "type": "chat.join" , 
                    "room_id" : room_id , 
                    "profile_image" : self.scope["user"].profile_image.url ,  
                    "username"  : self.scope["user"].username , 
                    "user_id"  : self.scope["user"].id , 
                }
            )
            
    async def leave_room(self , room_id)  : 
        room = await get_room_or_error(room_id , self.scope["user"])
        await disconnect_user(room, self.scope["user"])
        await self.channel_layer.group_send(
            room.group_name , 
            {
                "type" : "chat.leave" , 
                "room_id" : room_id , 
                "profile_image" : self.scope["user"].profile_image.url , 
                "username" : self.scope["user"].username , 
                "user_id" : self.scope["user"].id ,
            }
        )
        self.room_id = None
        await self.channel_layer.group_discard(
        room.group_name ,
        self.channel_name 
        )
        
        await self.send_json({
            "leave" : str(room.id)
        }
        )
        self.room_id = None
        
        
    async def chat_leave(self , event) : 
        if event["username"] : 
            await self.send_json({
                "msg_type" : MSG_TYPE_LEAVE , 
                "room" :  event["room_id"] , 
                "profile_image" : event["profile_image"] , 
                "username" : event["username"] , 
                "user_id" : event["user_id"] , 
                "message" : event["username"] + " disconnected." , 
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
        
        
    async def send_room(self,  room_id , message) :
        if self.room_id != None : 
            if str(room_id) != str(self.room_id) : 
                raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
        else : 
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
        room = await get_room_or_error(room_id , self.scope["user"])
        connected_users = room.connected_users.all()
        message = await create_room_chat_message(room , self.scope["user"] , message)
        
        await asyncio.gather(
            append_unread_msg_if_not_connected(room, room.user1, connected_users, message.content) ,
            append_unread_msg_if_not_connected(room, room.user2, connected_users, message.content)
        )
        user = self.scope["user"]
        await self.channel_layer.group_send(
            room.group_name ,
            {
                "type" : "chat_message" , 
                "message" : message , 
                "username" : user.username , 
                "profile_image" : user.profile_image.url , 
                "user_id" : user.id , 
                "message"  : message.content , 
                "msg_id" : message.id 
            }
        )
        
    async def chat_message(self , event) : 
        timestamp = calculateTimeStamp(timezone.now())
        await self.send_json({
            "msg_type" : MSG_TYPE_MESSAGE , 
            "message" : event["message"] ,
            "username":  event["username"] , 
            "user_id" : event["user_id"] , 
            "profile_image" : event["profile_image"] , 
            "natural_timestamp" : timestamp , 
            "msg_id" : event["msg_id"] ,
        })
        
        
    async def send_messages_payload(self, messages , new_page_number) : 
        await self.send_json({
            "messages_payload" : "messages_payload" , 
            "messages" : messages , 
            "new_page_number" : new_page_number ,
        })
        
    async def send_user_info_payload(self, user_info) :
        await self.send_json(
            user_info
        )
        
    async def display_progress_bar(self, is_displayed) : 
        await self.send_json({
            "display_progress_bar":  is_displayed ,
        })
        
@database_sync_to_async
def get_room_or_error(room_id , user) :
    try : 
        try : 
            room = PrivateChatRoom.objects.get(id = int(room_id))
        except PrivateChatRoom.DoesNotExist as e : 
            raise ClientError("INVALID ROOM" , "InValid room !")
        
        
        if user != room.user1 and user != room.user2 : 
            raise ClientError("ACCESS DENIED" , "You do not have permission to join this room !")
        friend_list = FriendList.objects.get(user = user).friends.all()
        if  not room.user1 in friend_list : 
            if not room.user2 in friend_list :
                raise ClientError("ACCESS DENIED" , "You must be friends to chat !")
    except ClientError as e : 
        self.handle_client_error(e)
    return room
@database_sync_to_async
def get_user_info(room , user) :
    try : 
        other_user = room.user1
        if other_user == user : 
            other_user = room.user2
        payload = {}
        s = LazyAccountEncoder()
        payload["user_info"] = s.serialize([other_user])[0]
        return payload
    except ClientError as e: 
        raise e 
        
    return None

@database_sync_to_async
def create_room_chat_message(room , user , message) : 
    return RoomChatMessage.objects.create(user = user , room = room , content = message)

@database_sync_to_async
def get_room_chat_messages(room , page_number) : 
    
    qs = RoomChatMessage.objects.by_room(room)
    p = Paginator(qs , DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)
    
    payload = {}
    new_page_number = int(page_number)
    if new_page_number <= p.num_pages : 
        new_page_number +=1 
        s = LazyChatRoomChatMessageEncoder()
        payload["messages"] = s.serialize(p.page(int(page_number)).object_list)
    else : 
        payload["messages"] = None
    payload["new_page_number"] = new_page_number
    return json.dumps(payload)

@database_sync_to_async
def connect_user(room , user)  : 
    account = Account.objects.get(id = user.id)
    return room.connect_user(account)

@database_sync_to_async
def disconnect_user(room , user):
    return room.disconnect_user(user)

@database_sync_to_async
def append_unread_msg_if_not_connected(room , user , connected_users , message) : 
    if not user in connected_users : 
        try : 
            unread_msgs = UnreadChatRoomMessages.objects.get(room = room , user = user)
            unread_msgs.most_recent_message = message[:80]
            unread_msgs.count += 1 
            unread_msgs.save()
        except UnreadChatRoomMessages.DoesNotExist : 
            UnreadChatRoomMessages(room = room , user = user , count = 1).save()
            pass
        
@database_sync_to_async
def on_user_connected(room , user) :
    connected_users = room.connected_users.all()
    
    if user in connected_users : 
        try : 
            unread_msgs = UnreadChatRoomMessages.objects.get(room = room , user = user)
            unread_msgs.count = 0 
            unread_msgs.save()
        except UnreadChatRoomMessages.DoesNotExist : 
            UnreadChatRoomMessages(room = room , user = user).save()
            pass
    return