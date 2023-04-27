from django.db import models
from django.conf import settings
from django.utils import timezone
from chat.utils import findOrCreatePrivateChat
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from notification.models import Notification

class FriendList(models.Model) :
    user            = models.OneToOneField(settings.AUTH_USER_MODEL ,
                                           on_delete = models.CASCADE ,
                                           related_name = "user")
    
    friends         = models.ManyToManyField(settings.AUTH_USER_MODEL , 
                                             blank = True , 
                                             related_name = "friends")
    # for reverse lookups .
    notifications   = GenericRelation(Notification , related_name = "notifications")
    
    def __str__(self) : 
        return self.user.username   
    
    def add_friend(self, account , *args , **kwargs ) : 
        # add a new friend in the friend list of the person 
        if not account in self.friends.all() : 
            self.friends.add(account)
            self.save() 
            
            content_type = ContentType.objects.get_for_model(self)
            self.notifications.create( 
                target = self.user  , 
                from_user = account , 
                redirect_url = f"{settings.BASE_URL}/account/{account.id}/" ,
                verb = f"You are now friends with {account.username}" , 
                content_type = content_type , 
                object_id = self.id ,  # id of the object of the table to which this is happening to  .
                content_object = self , 
            )
            self.save()
            
            chat = findOrCreatePrivateChat(self.user, account)
            if not chat.is_active : 
                chat.is_active = True
                chat.save()
                
    def remove_friend(self , account , *args , **kwargs ) : 
        # remove a new friend from the friend list
        if account in self.friends.all() : 
            self.friends.remove(account) 
            self.save()
            chat = findOrCreatePrivateChat(self.user, account)
            if chat.is_active : 
                chat.is_active = False
                chat.save()
    @property  
    def get_cname(self):
        # what kind of object we are working with . 
        return "FriendList"
    """
    username : "omkashyap007" 
    omkashyap007.unfrirend("some_bullshit_person") 
    omkashyap007 = self  , the current user whom i am working upon . 
    removee = that bullshit person basically . 
    """
          
    def unfriend(self, removee , *args , **kwargs ) : 
        # i am the remover and the person whom i am removing from my friend list will be the removee
        # intiate the action of unfriending the someone. 
        
        remover_friends_list = self # person terminating the friendship
        
        # remove friend from remover friend list
        remover_friends_list.remove_friend(removee)
        
        # remove from other person list myself 
        
        friends_list = FriendList.objects.get(user = removee)
        friends_list.remove_friend(self.user) 
        
        content_type = ContentType.objects.get_for_model(self)
        
        # create notification for the person who was removed , 
        self.notifications.create(
            target = removee  , 
            from_user = self.user , 
            redirect_url = f"{settings.BASE_URL}/account/{self.user.id}/" ,
            verb = f"You are no longer friends with {self.user.username}" , 
            content_type = content_type ,
            content_object = self ,
            object_id = self.id , 
        )
        # create notification for the remover 
        self.notifications.create(
            target = self.user, 
            from_user = removee , 
            redirect_url = f"{settings.BASE_URL}/account/{removee.id}/" ,
            verb = f"You are no longer friends with {removee.username}" , 
            content_type = content_type , 
            content_object = self , 
            object_id = self.id ,
        )
        self.save()
        
        
        
        
    def is_mutual_friend(self , friend) : 
        if friend in self.friends.all() : 
            return True
        return False
    
class FriendRequest(models.Model) : 
    """
    two parts invovled . 
    
    1 . SENDER  : 
        the person who sends the request to be friends . 
    
    2. RECEIVER :   
        the person who receives the request to be friend with the sender . 
    
    """
    
    sender                  = models.ForeignKey(settings.AUTH_USER_MODEL ,
                                                on_delete = models.CASCADE,
                                                related_name = "sender" )
    receiver                = models.ForeignKey(settings.AUTH_USER_MODEL , 
                                                on_delete = models.CASCADE , 
                                                related_name = "receiver")
    is_active               = models.BooleanField(default = True , blank = True , null = False)
    timestamp               = models.DateTimeField(auto_now_add = True)
    notifications           = GenericRelation(Notification , related_name = "notifications")
    
    def __str__(self) : 
        return str(self.sender.username) + " sent request to -> " + str(self.receiver.username)
    
    def accept(self) : 
        # accept a friend request . 
        # update friend list for both the sender and the receiver . 
        
        receiver_friend_list = FriendList.objects.get(user = self.receiver)
        
        if receiver_friend_list :
            content_type = ContentType.objects.get_for_model(self)
            receiver_notification = Notification.objects.get(target = self.receiver , object_id = self.id , content_type = content_type )
            receiver_notification.is_active = False
            receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.id}/"
            receiver_notification.verb = f"You accepted {self.sender.username}'s friend request !"
            receiver_notification.save()
            
            # add the person as a friend .
            receiver_friend_list.add_friend(self.sender)
            
            sender_friend_list = FriendList.objects.get(user = self.sender)
            if sender_friend_list : 
                
                 # create notification for the sender . 
                self.notifications.create(
                    target = self.sender , 
                    from_user = self.receiver , 
                    redirect_url = f"{settings.BASE_URL}/account/{self.receiver.id}/" ,
                    verb = f"{self.receiver.username}  accepted your friend request ." , 
                    content_type = content_type , 
                    content_object = self , 
                    object_id = self.id , 
                )
                        
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()
                
            return receiver_notification
                
    def decline(self) : 
        # decline the friend request . 
        # it is decline to is_active to false 
        
        self.is_active = False
        self.save()
        content_type = ContentType.objects.get_for_model(self)
            
        # update notification for receiver . 
        receiver_notification = Notification.objects.get(target = self.receiver , content_type = content_type , object_id = self.id )
        receiver_notification.is_active = False
        receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.id}/"
        receiver_notification.verb = f"You declined {self.sender.username}'s friend request !"
        receiver_notification.save()
        
        # create notification for the sender
        self.notifications.create(
            target = self.sender ,
            from_user = self.receiver , 
            redirect_url = f"{settings.BASE_URL}/account/{self.receiver.id}/" ,
            verb = f"{self.receiver.username}  declined your  friend request ." , 
            content_type = content_type , 
            content_object = self , 
            object_id = self.id ,  
        )
        
        return receiver_notification
    
    def cancel(self) : 
        self.is_active = False
        self.save()
        
        content_type = ContentType.objects.get_for_model(self)
        receiver_notification = Notification.objects.get(target = self.receiver , content_type = content_type , object_id = self.id)
        receiver_notification.is_active = False
        receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.id}/"
        receiver_notification.verb = f"{self.sender.username} cancelled the friend request sent to you !"
        receiver_notification.save()
        
        # create notification for the sender
        self.notifications.create(
            target = self.sender , 
            from_user = self.receiver , 
            redirect_url = f"{settings.BASE_URL}/account/{self.receiver.id}/" ,
            verb = f"You cancelled the friend request to {self.receiver.username}. " , 
            content_type = content_type , 
        )
        self.save()
        return receiver_notification
        
    @property
    def get_cname(self):
        return "FriendRequest"
        
        
        
"""

class FriendList(model.Model) : 
    user 
    friends 
    
object = [<FriendList:user>]

so this object has the information about the particular user and his friend list

user = omkashyap007
user.friendlist.friends


the model will be referenced to get the friends . 

friend_list = FriendList(user = omkashyap007)

so the friend_list will be the object of the friend_list

self = friend_list here . 
self.user
self.friends

are the two attributes . 

now for add_friend 

self , account

self = object of friend list 

self.friends.add(account)

user = request.user
friend_list = FriendList.objects.get(user = user)


"""