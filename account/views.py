from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, LoginForm, AccountUpdateForm
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from account.models import Account

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage

import os
import cv2
import json
import base64
import requests
from django.core import files


from friend.models import FriendList , FriendRequest
from friend.utils import get_friend_request_or_false
from friend.friend_request_status import FriendRequestStatus


TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

# Create your views here.


def get_error_dict(error_dict):
    l = []
    for error_field in error_dict:
        for error in error_dict[error_field]:
            l.append(error)
    return l


def accountView(request, user_id, *args, **kwargs):
    context = {}
    user_id = int(user_id)

    try:
        account = Account.objects.get(id=user_id)
    except Exception as e:
        return HttpResponse("The account does not exist !")
    if account:
        context["id"] = account.id
        context["username"] = account.username
        context["email"] = account.email
        context["profile_image"] = account.profile_image.url
        context["hide_email"] = account.hide_email
        context["request_sent"] = None
        context["friend_requests"] = None
        context["is_self"] = None
        context["is_friend"] = None
        request_sent = None
        friend_requests = None
        


        try :
            friend_list = FriendList.objects.get(user = account)
        except FriendList.DoesNotExist :
            friend_list = FriendList(user = account)
            friend_list.save()
        friends = friend_list.friends.all()
        context["friends"] = friends


        # state template

        
        """

        The states which we  will be seeing in the profile . 


        1 . is_self :  (**1**)
                True : 
                    CRUD on you

                False : 
                    state (**2**)

        2 .  is_friend (**2**)
                True : message em -> 
                
                False : 
                    state (**3**)
        3 . 
            is_not_friend : 
                1. No_request_was_sent_from_either_side
                
                2 . You send them a friend request :
                    Cancel it if you want .
                    
                    
                3. They sent you a friend request : 
                    decline , accpet 




        """


        is_self = False
        is_friend = False

        user = request.user
        
        if user.is_authenticated and user == account : 
            is_self = True
            print("You are looking at your own account") 
        if user.is_authenticated and not is_self : 
            
            if user in friends : # friends.filter(id = user.id) 
                is_friend = True
            else : 
                is_friend = False
                # the three cases will be seen . 
                # 1. no request sent from either side . 
                # 2 . you sent them request .
                # 3. they sent you the request . 


                # did he send you the friend request . 
                # account one is the sender 
                # i am the user . current 
                
                if get_friend_request_or_false(sender = account, receiver = user ) != False : 
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context["pending_friend_request_id"] = get_friend_request_or_false(sender = account, receiver = user).id
                    
                # you sent him a friend request or not
                elif get_friend_request_or_false(sender = user , receiver = account) != False : 
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                else : 
                  request_sent = FriendRequestStatus.NO_REQUEST_SENT.value  
                
        elif not user.is_authenticated : 
            is_self = False

        else : 
            try : 
                friend_requests = FriendRequest.objects.filter(receiver = user , is_active = True)
            except : 
                ...
        


        # is_self = True
        # is_friend = False
        # user = request.user
        # if user.is_authenticated and user != account:
        # 	is_self = False
        # 	if friends.filter(pk = user.id) :
        # 		is_friend = True

        # 	else  :
        # 		is_friend = False
        # elif not user.is_authenticated:
        # 	is_self = False

        context["is_self"] = is_self
        context["is_friend"] = is_friend
        context["request_sent"] = request_sent
        context["friend_requests"] = friend_requests

        return render(request, "account/account.html", context)


def account_search_view(request, *args, **kwargs):
    context = {}
    if request.method == "GET":
        search_query = request.GET.get("q")
        if len(search_query) > 0:
            search_results = Account.objects.filter(
                email__icontains=search_query
            ).filter(
                username__icontains=search_query
            ).distinct()
            user= request.user
            accounts = []
            # structure = accounts = [ (account , is_friend_boolean) ]
            if user.is_authenticated : 
                friendList = FriendList.objects.get(user = user)
                for search_user in search_results : 
                    if friendList.is_mutual_friend(search_user) : 
                        accounts.append((search_user , True))
                    else: 
                        accounts.append((search_user,False ))  # you have no friends .
            else :
                return redirect("login")
            context["accounts"] = accounts

    return render(request, "account/search_results.html", context)


def editAccountView(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = int(kwargs.get("user_id"))
    try:
        account = Account.objects.get(id=user_id)
    except Account.DoesNotExist :
        return HttpResponse("<div style = 'color : red ; ' >Ooops .. Something went wrong !</div>")
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone elses profile.")
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # delete the old profile image so the name is preserved.
            # account.profile_image.delete()
            form.save()
            return redirect("account:view", user_id=account.pk)
        else:
            form = AccountUpdateForm(request.POST , instance = request.user ,
                initial={
                    "id": account.pk,
                    "email": account.email,
                    "username": account.username,
                    "profile_image": account.profile_image,
                    "hide_email": account.hide_email,
                }
            )
            context['form'] = form
    else:
        form = AccountUpdateForm(
            initial={
                    "id": account.pk,
                    "email": account.email,
                    "username": account.username,
                    "profile_image": account.profile_image,
                    "hide_email": account.hide_email,
                }
            )
        context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "account/edit_account.html", context)




# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------



# receiving the image dimensions from the front end and then saving it to the temporary file

# converting it to base 64 and then storing it to local storage .

# then cropping it via open cv .




def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        print("exception: " + str(e))
        # workaround for an issue I found
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
    return None


def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            # print(imageString)
            # this is base64 image which needs to be converted to image .
            url = save_temp_profile_image_from_base64String(imageString, user)

               # here the image is converted into the real image with pixels representing the arrays of rgb
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))
            if cropX < 0:
                cropX = 0
            if cropY < 0: # There is a bug with cropperjs. y can be negative.
                cropY = 0

            crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]

            cv2.imwrite(url, crop_img)

            # delete the old image
            user.profile_image.delete()

            # Save the cropped image to user model
            user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            user.save()

            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url

            # delete temp file
            os.remove(url)

        except Exception as e:
            print("exception: " + str(e))
            payload['result'] = "error"
            payload['exception'] = str(e)


    return HttpResponse(json.dumps(payload), content_type="application/json")



def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    account = Account.objects.get(pk=user_id)
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone elses profile.")
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account:view", user_id=account.pk)
        else:
            form = AccountUpdateForm(request.POST, instance=request.user,
                initial={
                    "id": account.pk,
                    "email": account.email,
                    "username": account.username,
                    "profile_image": account.profile_image,
                    "hide_email": account.hide_email,
                }
            )
            context['form'] = form
    else:
        form = AccountUpdateForm(
            initial={
                    "id": account.pk,
                    "email": account.email,
                    "username": account.username,
                    "profile_image": account.profile_image,
                    "hide_email": account.hide_email,
                }
            )
        context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "account/edit_account.html", context)




# cropping and the saving the image is done .


# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------







# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------

# authentication system from here .

def registerUser(request , *args , **kwargs) :
    if request.user.is_authenticated :
        messages.error(request , "You are already authenticated !")
        return redirect("home")

    form = RegistrationForm()

    if request.method == "POST" :
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request , user, backend = "account.backends.CaseInsensitiveModelBackend")

            destination = get_redirect_if_exists(request)
            if destination : # if destination != None
                return redirect(destination)
            return redirect("home")
    context = {
        "registration_form" : form ,
    }
    return render(request , "account/register.html" , context)



def loginUser(request , *args , **kwargs) :
    if request.user.is_authenticated :
        return redirect("home")

    form = LoginForm()
    errors = []
    if request.method == "POST" :
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            if user :
                return redirect("home")
            if not user :
                messages.error(request , "The password is Invalid !")
        else :
          errors = get_error_dict(form.errors)
    context = {
        "form" : form ,
        "errors" : errors ,
    }
    return render(request , "account/login.html" , context)



def logoutUser(request , *args , **kwargs ) :
    if request.user.is_authenticated :
        logout(request)
    else :
        messages.error(request , "You are not authenticated !")
    return redirect("home")


def get_redirect_if_exists(request) :
    redirect= None
    if request.GET :
        if request.GET.get("next") :
            redirect = str(request.GET.get("next"))
    return redirect



# auth system ends .

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------