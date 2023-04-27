from django.dispatch import receiver
from .models import UnreadChatRoomMessages , PrivateChatRoom
from django.db.models.signals import post_save , pre_save
from notification.models import Notification
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone


@receiver(post_save, sender = PrivateChatRoom)
def createUnreadChatRoomMessagesObject(sender, instance , created , **kwargs):
    if created : 
        unread_msgs1 = UnreadChatRoomMessages(room = instance , user = instance.user1)
        unread_msgs1.save()
        
        unread_msgs2 = UnreadChatRoomMessages(room = instance , user = instance.user2)
        unread_msgs2.save()
    
@receiver(pre_save , sender = UnreadChatRoomMessages)
def incrementUnreadMessageCount(sender , instance , **kwargs):
    if instance.id == None : 
        pass
    else : 
        previous = UnreadChatRoomMessages.objects.get(id = instance.id)
        if previous.count < instance.count : 
            content_type = ContentType.objects.get_for_model(instance)
            if instance.user == instance.room.user1 : 
                other_user = instance.room.user2
            else : 
                other_user = instance.room.user1
            try : 
                notification = Notification.objects.get(target = instance.user , content_type = content_type , object_id = instance.id )
                notification.verb = instance.most_recent_message
                notification.timestamp = timezone.now()
            except Notification.DoesNotExist : 
                instance.notifications.create(
                    target = instance.user , 
                    from_user = other_user , 
                    redirect_url = f"{settings.BASE_URL}/chat/?room_id={instance.room.id}/" , 
                    verb = instance.most_recent_message , 
                    content_type = content_type 
                )
                
@receiver(pre_save , sender = UnreadChatRoomMessages)
def removeUnreadMessageCountNotification(sender , instance , **kwargs):
    """
    If the unread message count decreases , it means the user joined the chat , So delete the notification 
    """
    if instance.id == None : 
        pass
    else : 
        previous = UnreadChatRoomMessages.objects.get(id = instance.id) 
        if previous.count > instance.count : 
            content_type = ContentType.objects.get_for_model(instance)
            try : 
                notification = Notification.objects.get(target = instance.user , content_type = content_type, object_id = instance.id )
                notification.delete()
            except Notification.DoesNotExist : 
                pass