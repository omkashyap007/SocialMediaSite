from django.shortcuts import render
from django.contrib import messages
from django.conf import settings

def HomeScreenView(request,  *args , **kwargs) : 
    context = {}
    context["room_id"] =1 
    context["debug_mode"] = settings.DEBUG
    return render(request , "personal/home.html" , context) 