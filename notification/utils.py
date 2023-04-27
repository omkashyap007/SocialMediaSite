from django.core.serializers.python import Serializer
from django.core.serializers import serialize
from django.contrib.humanize.templatetags.humanize import naturaltime

class LazyNotificationEncoder(Serializer):
    """
    Serialize a notification in JSON
    1. FriendRequest-
    2. Friendist
    3. UnreadChatRoomMessage
    """
    
    def get_dump_object(self , object):
        dump_object = {}
        if object.get_content_object_type() == "FriendRequest" : 
            dump_object = {
                "notification_type"     : object.get_content_object_type() , 
                "notification_id"       : str(object.id) , 
                "verb"                  : str(object.verb) , 
                "is_active"             : str(object.content_object.is_active) , 
                "is_read"               : str(object.read) ,
                "natural_timestamp"     : str(naturaltime(object.timestamp)) , 
                "timestamp"             : str(object.timestamp) , 
                "actions"               : {
                    "redirect_url"      : str(object.redirect_url) , 
                },  
                "from"                  : {
                    "image_url"         : str(object.from_user.profile_image.url) , 
                } ,
                
            }
        if object.get_content_object_type() == "FriendList":
            dump_object = {
                "notification_type"     : object.get_content_object_type() , 
                "notification_id"       : str(object.id) , 
                "verb"                  : str(object.verb) , 
                "is_read"               : str(object.read) ,
                "natural_timestamp"     : str(naturaltime(object.timestamp)) , 
                "timestamp"             : str(object.timestamp) , 
                "actions"               : {
                    "redirect_url"      : str(object.redirect_url) , 
                },  
                "from"                  : {
                    "image_url"         : str(object.from_user.profile_image.url) , 
                } ,
                
            }
            
        if object.get_content_object_type() == "UnreadChatRoomMessages":
            dump_object = {
                "notification_type"     : object.get_content_object_type() , 
                "notification_id"       : str(object.id) , 
                "verb"                  : str(object.verb) , 
                "natural_timestamp"     : str(naturaltime(object.timestamp)) , 
                "timestamp"             : str(object.timestamp) , 
                "actions"               : {
                    "redirect_url"      : str(object.redirect_url) , 
                },  
                "from"                  : {
                    "title"             : str(object.content_object.get_other_user.username) ,
                    "image_url"         : str(object.from_user.profile_image.url) , 
                } ,
                
            }
        return dump_object
    
