from django.core.serializers.python import Serializer

class LazyAccountEncoder(Serializer) :
    def get_dump_object(self , object) : 
        dump_object = {}
        dump_object.update({"id" : str(object.id)})
        dump_object.update({"email" : str(object.email)})
        dump_object.update({"username" : str(object.username)})
        dump_object.update({"profile_image" : str(object.profile_image.url)})
        return dump_object
    
    