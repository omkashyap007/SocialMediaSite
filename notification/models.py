from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    # the user who will recieve the notification 
    target              = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.CASCADE)
    
    # the user who has created the notification 
    from_user           =  models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.CASCADE , 
                                             blank = True , null = True , unique = False , related_name = "from_user")
    
    redirect_url        = models.URLField(max_length = 500 , null = True , blank = True ,
                                          unique = False)
    
    # the statement which will describe what is going on in the notification (Om sent friend request to you)
    
    verb                = models.CharField(max_length = 255 , unique = False , blank = True , null = True)
    timestamp           = models.DateTimeField(auto_now_add = True)
    read                = models.BooleanField(default = False)
    
    content_type        = models.ForeignKey(ContentType , on_delete = models.CASCADE)
    object_id           = models.PositiveIntegerField()
    content_object      = GenericForeignKey()
    
    def __str__(self): 
        return str(self.verb)
    
    def get_content_object_type(self):
        return str(self.content_object.get_cname)
    
    