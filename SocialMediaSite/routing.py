from channels.routing import URLRouter , ProtocolTypeRouter 
from channels.auth import AuthMiddlewareStack 
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from public_chat.consumers import PublicChatConsumer
from chat.consumers import ChatConsumer
from notification.consumers import NotificationConsumer
application = ProtocolTypeRouter(
    {
        "websocket" : AuthMiddlewareStack(
            AllowedHostsOriginValidator(
                URLRouter(
                    [
                        path("" , NotificationConsumer.as_asgi()) , 
                        path("chat/<int:room_id>/" , ChatConsumer.as_asgi()) , 
                        path("public_chat/<int:room_id>/" , PublicChatConsumer.as_asgi()),
                    ]
                )
            )
        )
    }
)