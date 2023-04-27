from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FriendRequest
from django.contrib.contenttypes.models import ContentType
from django.conf import settings  
from notification.models import Notification

@receiver(post_save , sender = FriendRequest)
def create_notification(sender , instance , created , **kwargs):
    if created :
        try :
            notification = Notification.objects.create(
                target = instance.receiver , 
                from_user = instance.sender , 
                redirect_url = f"{settings.BASE_URL}/account/{instance.sender.id}/" , 
                verb = f"{instance.sender.username} sent you a friend request  !" , 
                content_type = ContentType.objects.get_for_model(instance) , 
                content_object  = instance ,
                object_id = instance.id , 
            )
            notification.save()
        except Exception as e:
            print(f"There is an error : {e}")