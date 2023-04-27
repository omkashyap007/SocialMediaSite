from django.db import models
from django.conf import settings 

class PublicChatRoom(models.Model):
    title                   = models.CharField(max_length = 255 , unique = True , blank = False)
    users                   = models.ManyToManyField(settings.AUTH_USER_MODEL ,
                                                     blank = True , 
                                                     help_text = "Users who are connected to the chat room !")

    def __str__(self) : 
        return str(self.title)
    
    def connect_user(self , user): 
        is_user_added = False
        if not user in self.users.all() : 
            self.users.add(user)
            self.save()
            is_user_added = True
        elif user in self.users.all(): 
            is_user_added = True
        return is_user_added

    def disconnect_user(self , user) : 
        is_user_removed = False
        if user in self.users.all(): 
            self.users.remove(user)
            self. save()
            is_user_removed = True
        elif user not in self.users.all()  : 
            is_user_removed = True
        return is_user_removed 
    
    @property
    def group_name(self) : 
        """
        Return the channels group name that sockets should subscribe to and get the sent messages as they are generated . 
        """
        return f"PublicChatRoom_{self.id}"
    
class PublicChatRoomMessageManager(models.Manager):
    
    def another_by_room(self , room) : 
        qs = self.get_queryset().filter(room = room).order_by("-timestamp")
        return qs 
    
    def by_room(self , room) : 
        qs = PublicRoomChatMessage.objects.filter(room = room).order_by("-timestamp")
        return qs
        """
        how will this work . 
        and in which thing it will be applied 
        
        1. this will return the messages on basis of objects.  
        how we normally do is : 
        messages = PublicRoomChatMessage.objects.all().filter(room = room)
        but  now "I" think it will directly work without it . 
        
        
        
        2. it will be applied on the objects . because it is the manager class . 
        objects.by_room(room) -> this thing . 
        
        PublicRoomChatMessage.objects.by_room(room) this will return the queryset on the basis of the room . 
        will see. and also this will have the queryset arranged on the basis of the timestamp . 
        """
class PublicRoomChatMessage(models.Model): 
    """
    chat messagers created by the user inside a chat room  
    """
    user                    = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.CASCADE)
    room                    = models.ForeignKey(PublicChatRoom , on_delete = models.CASCADE)
    timestamp              = models.DateTimeField(auto_now_add = True)
    content                 = models.TextField(blank = False , unique = False)
    objects                 = PublicChatRoomMessageManager()
    def __str__(self) : 
        return self.content
    
    