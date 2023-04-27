import json
from datetime import datetime
from django.conf import settings
from notification.constants import *
from chat.exceptions import ClientError
from django.core.paginator import Paginator
from notification.models import Notification
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from chat.models import UnreadChatRoomMessages
from friend.models import FriendList , FriendRequest
from notification.utils import LazyNotificationEncoder
from django.contrib.contenttypes.models import ContentType
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("Notification conusmer  connected user : " + self.scope["user"].username )
        await self.accept()

    async def disconnect(self , close_code):
        print("Notification socket disconnected ")
        
    async def receive_json(self , content):
        command = content.get("command" , None)
        
        print("Notification receive command : " + command)  
        try : 
            if command == "get_general_notifications" : 
                payload = await get_general_notifications(self.scope["user"], content["page_number"]) 
                if payload == None :
                    await self.general_pagination_exhausted()  
                else : 
                    await self.send_general_notifications_payload(payload["notifications"] , payload["new_page_number"])
                    
            elif command == "accept_friend_request" : 
                notification_id = content["notification_id"]
                payload = await accept_friend_request(self.scope["user"] , notification_id)
                if payload == None : 
                    raise ClientError(204 , "Something went wrong . Try refreshing your browser !")
                else : 
                    payload = json.loads(payload)
                    await self.send_updated_friend_request_notification(payload["notification"])
                    
            elif command == "decline_friend_reqeust" : 
                notification_id = content["notification_id"]
                payload = await decline_friend_request(self.scope["user"] , notification_id)
                if payload == None : 
                    raise ClientError(204 , "Something went wrong . Try refreshing your browser !")
                else : 
                    payload = json.loads(payload)
                    await self.send_updated_friend_request_notification(payload["notification"])
            elif command == "refresh_general_notifications" :
                payload = await refresh_general_notifications(self.scope["user"], content["oldest_timestamp"], content["newest_timestamp"])
                
                if not payload :
                    await self.send_json({
                        "general_msg_type" : NO_NEW_GENERAL_NOTIFICAIONS_FOR_THE_USER , 
                    })
                if payload : 
                    await self.send_general_refreshed_notifications_payload(payload["notifications"])
                
            elif command == "get_new_general_notifiactions":
                payload = await get_new_general_notifications(self.scope["user"], content["newest_timestamp"])
                if payload  :
                    await self.send_new_general_notifications_payload(payload["notifications"])
                
            elif command == "get_unread_general_notifications_count" : 
                print("This command was run!")
                payload = await get_unread_general_notifications_count(self.scope["user"])
                if payload != None : 
                    await self.send_unread_general_notification_count(payload["count"])
            elif command == "mark_notifications_read" : 
                await mark_notifications_read(self.scope["user"])
                
            elif command == "get_chat_notifications" :
                payload = await get_chat_notifications(self.scope["user"] , content["page_number"])
                if not payload :
                    print("No new chat message")
                else : 
                    await self.send_chat_notfiactions_payload(payload["notifications"], payload["new_page_number"])
            
        except ClientError as e : 
            print("There is  an error : " + str(e.message))
            await self.handle_client_error(e)
        
        
    async def handle_client_error(self , e) :      
        await self.send_json({
            "notification_error" : True , 
            "error_message" : e.message , 
        })
        
        
        
    async def display_progress_bar(self , shouldDisplay):
        print("Notification : display progress bar : " + str(shouldDisplay))
        await self.send_json({
            "progess_bar" : shouldDisplay , 
        })
        
        
        
    async def send_general_notifications_payload(self,  notifications , new_page_number):
        await self.send_json({
            "general_msg_type" : GENERAL_MSG_TYPE_NOTIFICATIONS_PAYLOAD , 
            "notifications" : notifications , 
            "new_page_number" : new_page_number , 
        })

    async def send_updated_friend_request_notification(self, notification) : 
        """
        After the friend request is accepted or declined , send the updated notification to template .
        payload contains 'notifications' and 'response 
        """
        await self.send_json({
            "general_msg_type" : GENERAL_MSG_TYPE_UPDATED_NOTIFCATION ,
            "notification" :  notification , 
        })
        
    async def general_pagination_exhausted(self):
        await self.send_json({
            "general_msg_type":  GENERAL_MSG_TYPE_PAGINATION_EXHAUSTED , 
            
        })
        
    async def send_general_refreshed_notifications_payload(self , notifications) : 
        await self.send_json({
            "general_msg_type" : GENERAL_MSG_TYPE_NOTIFICATIONS_REFRESH_PAYLOAD , 
            "notifications" : notifications , 
        })
        
    async def send_new_general_notifications_payload(self , notifications):
        await self.send_json({
            "general_msg_type" : GENERAL_MSG_TYPE_GET_NEW_NOTIFICATIONS , 
            "notifications" : notifications , 
        })
        
    async def send_unread_general_notification_count(self, count) :
        print("The message was sent!")
        print(count)
        await self.send_json({
            "general_msg_type" : GENERAL_MSG_TYPE_GET_UNREAD_NOTIFICATIONS_COUNT , 
            "count" : count , 
        })

    async def send_chat_notfiactions_payload(self, notifications , new_page_number) : 
        await self.send_json({
            "chat_msg_type" : CHAT_MSG_TYPE_NOTIFICATIONS_PAYLOAD , 
            "notifications" : notifications , 
            "new_page_number" : new_page_number , 
        })


# django orm and sync to async functions for the data . 
@database_sync_to_async
def get_general_notifications(user , page_number):
    """
    General notifications for the two models
    1. FriendReqeust
    2. FriendList
    these will be appended to the bottom 
    """
    if user.is_authenticated : 
        friend_request_ct       = ContentType.objects.get_for_model(FriendRequest)
        friend_list_ct          = ContentType.objects.get_for_model(FriendList)
        notifications           = Notification.objects.filter(target = user , content_type__in = [
            friend_request_ct , friend_list_ct]).order_by("-timestamp")
        p = Paginator(object_list = notifications ,per_page =  DEFAULT_NOTIFICATION_PAGE_SIZE)
        payload = {}
        page_number = int(page_number)
        if len(notifications)>0 :
            if page_number <= p.num_pages : 
                s = LazyNotificationEncoder()
                serialized_notifications = s.serialize(p.page(page_number).object_list)
                payload["notifications"] = serialized_notifications
                new_page_number = int(page_number) +1
                payload["new_page_number"] = new_page_number
            if not payload : 
                return None
        else : 
            return None
    else : 
        raise ClientError(204 , "User must be authenticated to get the data !")
    return payload


@database_sync_to_async
def accept_friend_request(user , notification_id):
    if user.is_authenticated : 
        try : 
            notification = Notification.objects.get(id = notification_id)
            friend_request = notification.content_object
            payload = {}
            if friend_request.receiver == user :
                updated_notification = friend_request.accept()
                s = LazyNotificationEncoder()
                payload["notification"] = s.serialize([updated_notification])[0]
                return  json.dumps(payload)
                
        except Notification.DoesNotExist : 
            raise ClientError(422 , "An error occured with that notification. Try refreshing the browser.")
        return None
    
    
@database_sync_to_async
def decline_friend_request(user , notification_id):
    if user.is_authenticated : 
        try : 
            notification = Notification.objects.get(id = notification_id)
            friend_request = notification.content_object
            payload = {}
            if friend_request.receiver == user :
                updated_notification = friend_request.decline()
                s = LazyNotificationEncoder()
                payload["notification"] = s.serialize([updated_notification])[0]
                return  json.dumps(payload)
                
        except Notification.DoesNotExist : 
            raise ClientError(422 , "An error occured with that notification. Try refreshing the browser.")
        return None
    
@database_sync_to_async
def refresh_general_notifications(user , oldest_timestamp , newest_timestamp) : 
    payload={}
    if user.is_authenticated :
        oldest_ts = oldest_timestamp[0:oldest_timestamp.find("+")]
        oldest_ts = datetime.strptime(oldest_ts , "%Y-%m-%d %H:%M:%S.%f")
        newest_ts = newest_timestamp[0:newest_timestamp.find("+")]
        newest_ts = datetime.strptime(newest_ts , "%Y-%m-%d %H:%M:%S.%f")
        
        friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
        friend_list_ct = ContentType.objects.get_for_model(FriendList)
        
        notifications = Notification.objects.filter(target = user  ,  content_type__in = [
            friend_request_ct , friend_list_ct ] , timestamp__gte = oldest_ts , timestamp__lte = newest_ts).order_by("-timestamp")
        
        s = LazyNotificationEncoder()
        payload["notifications"] = s.serialize(notifications)
    else : 
        raise ClientError(204, "User must be authenticated to get the notifications !")
    return payload

@database_sync_to_async
def get_new_general_notifications(user , newest_timestamp) :
    payload = {}
    if user.is_authenticated :
        timestamp = newest_timestamp[0:newest_timestamp.find("+")]
        timestamp = datetime.strptime(timestamp , "%Y-%m-%d %H:%M:%S.%f")
        
        friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
        friend_list_ct = ContentType.objects.get_for_model(FriendList)
        
        notifications = Notification.objects.filter(target = user  ,  content_type__in = [
            friend_request_ct , friend_list_ct ] , timestamp__gt = timestamp ,read = False).order_by("-timestamp")
        
        s = LazyNotificationEncoder()
        payload["notifications"] = s.serialize(notifications)
        print(payload)
        return  payload
    else  : 
        raise  ClientError(204,"User must be authenticated to get notification !")
    
@database_sync_to_async
def get_unread_general_notifications_count(user) :
    payload = {}
    if user.is_authenticated : 
        friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
        friend_list_ct = ContentType.objects.get_for_model(FriendList)
        
        notifications = Notification.objects.filter(target = user  ,  content_type__in = [
            friend_request_ct , friend_list_ct ],read = False)
        unread_count = 0
        if notifications : 
            for notification in notifications : 
                if not notification.read : 
                    unread_count+=1
        payload["count"] = unread_count
        print(f"The payload with unread count of notifications {payload}")
        return payload
    else :  
        raise ClientError(204,"User must be authentictaed to get the notifications !")
    print(payload)
    return None

@database_sync_to_async
def mark_notifications_read(user) :
    if user.is_authenticated  : 
        notifications = Notification.objects.filter(target = user)
        for notification in notifications :
            notification.read = True
            notification.save()
    return 
            
@database_sync_to_async
def get_chat_notifications(user , page_number) :
    """
    Get Chat Notifications with Pagination ( next page of results ) .
    This is for appending to the bottom of the notifications list . 
    Chat Notifications are : 
        1. UnreadChatRoomMessages
    """
    payload = {}
    if user.is_authenticated : 
        chatmessage_ct = ContentType.objects.get_for_model(UnreadChatRoomMessages)
        notifications = Notification.objects.filter(target = user , content_type = chatmessage_ct).order_by("-timestamp")
        p = Paginator(notifications , DEFAULT_NOTIFICATION_PAGE_SIZE)
        if len(notifications) > 0 : 
            page_number = int(page_number)
            if int(page_number) <= p.num_pages :
                s = LazyNotificationEncoder()
                serialized_notifications = s.serialize(p.page(page_number).object_list)
                payload["notifications"] = serialized_notifications
                new_page_number = page_number + 1
                payload["new_page_number"] = new_page_number
        else : 
            payload = {}
    else : 
        raise ClientError(204 , "User must be authenticated to access the chat messages notifications !")
    return payload