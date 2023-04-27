from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from notification.models import Notification


User = settings.AUTH_USER_MODEL

class PrivateChatRoom(models.Model):
    user1               = models.ForeignKey(User , 
                                            on_delete = models.CASCADE ,
                                            related_name = "user1")
    user2               = models.ForeignKey(User ,
                                            on_delete = models.CASCADE ,
                                            related_name = "user2")
    connected_users     = models.ManyToManyField(User , blank = True ,  related_name = "connected_users") 
    
    is_active           = models.BooleanField(default = True)
    
    def __str__(self) : 
        return f"Chat between {self.user1} and {self.user2}"
    
    def connect_user(self, user):
        """
        return True if user is added to the connected_users list . 
        """
        is_user_added = False
        if not user in self.connected_users.all() :
            self.connected_users.add(user)
            is_user_added = True
        return is_user_added
    
    def disconnect_user(self, user) :
        is_user_removed = False
        if user in self.connected_users.all() :
            self.connected_users.remove(user)
            is_user_removed = True
        return is_user_removed
    
    
    @property
    def group_name(self):
        return f"PrivateChatRoom_{self.id}"
    
    
class RoomChatMessagesManager(models.Manager):
    def by_room(self , room) : 
        queryset = RoomChatMessage.objects.filter(room = room).order_by("-timestamp")
        return queryset
    
class RoomChatMessage(models.Model):
    user                = models.ForeignKey(User , on_delete = models.CASCADE)
    room                = models.ForeignKey(PrivateChatRoom , on_delete = models.CASCADE)
    timestamp           = models.DateTimeField(auto_now_add = True)
    content             = models.TextField(unique = False , blank = False)
    
    objects             = RoomChatMessagesManager()
    
class UnreadChatRoomMessages(models.Model):
    """
    Keep track of the number of unread messages by  a specific user in a specific private chat.
    when the user connects the chat room , the messages will be considered "read" and "count" will be set to 0 .
    """
    room                = models.ForeignKey(PrivateChatRoom , on_delete = models.CASCADE , related_name = "room")
    user                = models.ForeignKey(User , on_delete = models.CASCADE)
    count               = models.PositiveIntegerField(default =0)
    most_recent_message = models.CharField(max_length = 100 , blank = True , null = True)
    reset_timestamp     = models.DateTimeField()
    notifications       = GenericRelation(Notification)
    
    def __str__(self):
        return f"Messages that {str(self.user.username)} has not read yet !"
    
    def save(self , *args ,**kwargs):
        if not self.id : 
            self.reset_timestamp = timezone.now()
        return super(UnreadChatRoomMessages , self).save(*args , **kwargs)
    
    @property
    def get_cname(self):
        return "UnreadChatRoomMessages"
    
    @property
    def get_other_user(self):
        if self.user == self.room.user1 : 
            return self.room.user2
        return self.room.user1
