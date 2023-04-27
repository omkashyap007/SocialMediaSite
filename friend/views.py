from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from account.models import Account
from friend.models import FriendRequest, FriendList


def friend_list_view(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        if user_id != None:
            try:
                this_user = Account.objects.get(id=user_id)
                context["this_user"] = this_user
            except Account.DoesNotExist:
                return HttpResponse("The user does not exist !")
            try:
                friendList = FriendList.objects.get(user=this_user)
                # this is the friend list of the user whom we are checking.
                # this is the person whom we are visiting and seeing his friend list .
                # this will tell that if the person in his is list is mututal with the
                # one who is checking the this_user .
            except FriendList.DoesNotExist:
                return HttpResponse("Cannot find the firend list for the user : {}".format(this_user.username))

            if user != this_user:
                if not user in friendList.friends.all():
                    return HttpResponse("You must be friends to the user to view their friend list !")
            friends = []
            auth_user_friend_list = FriendList.objects.get(user=user)
            # this is the friend list of the current user who is checking the friend list.

            for friend in friendList.friends.all():
                # all the friends of the the_user . we will check for the mutual friendship
                # in both the friend list.
                friends.append(
                    (friend, auth_user_friend_list.is_mutual_friend(friend)))
            context["friends"] = friends
        else:
            return HttpResponse("You are viewing friend list of person who does not exist !")
    else:
        return HttpResposne("You must be authenticated to see the friend list of a user !")
    return render(request, "friend/friend_list.html", context)


def friend_requests(request, *args, **kwargs):
    context = {}
    user = request.user

    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        account = Account.objects.get(pk=user_id)

        if account == user:
            friend_requests = FriendRequest.objects.filter(
                receiver=account, is_active=True)

            context["friend_requests"] = friend_requests
        else:
            return HttpResponse("You can't view another users friend requests !")
    else:
        return redirect("login")
    return render(request, "friend/friend_requests.html", context)


def send_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}

    if request.method == "POST" and user.is_authenticated:
        # the ajax request will be a post request containing all the variables in it .
        user_id = request.POST.get("receiver_user_id")
        user_id = int(user_id)
        if user_id:
            receiver = Account.objects.get(pk=user_id)
            # you are definitely the sender . the sender of the friend request .
            # receiver is the person who will receive the friend request , or the person whom you are sending the friend request .
            try:
                friend_requests = FriendRequest.objects.filter(
                    sender=user, receiver=receiver)
                # all the friend requests between the sender and receiver .
                try:
                    for request in friend_requests:
                        print(f"The request is : {request}")
                        if request.is_active:
                            print(f"The request {request}  is active !")
                            raise Exception("You already sent them a friend request !")
                            # if any request in the queryset is active , then raise exception that there are already existing friend requests .
                        else:
                            ...
                    friend_request = FriendRequest(
                        sender=user, receiver=receiver)
                    friend_request.save()
                    payload["response"] = "Friend request sent"
                    print("Friend request sent")
                except Exception as e:
                    payload["reponse"] = str(e)

            except FriendRequest.DoesNotExist:
                friend_request = FriendRequest(sender=user, receiver=receiver)
                friend_request.save()
                payload["response"] = "Friend request  sent"

        else:
            payload["response"] = "Unable to send a friend request"
    else:
        payload["response"] = "You must be authenticated to send a friend request !"

    return HttpResponse(json.dumps(payload), content_type="application/json")


def accept_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "GET" and user.is_authenticated:

        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            # confirm that is the correct request
            if friend_request.receiver == user:
                if friend_request:
                    # found the request. Now accept it
                    updated_notification = friend_request.accept()
                    payload['response'] = "Friend request accepted."

                else:
                    payload['response'] = "Something went wrong."
            else:
                payload['response'] = "That is not your request to accept."
        else:
            payload['response'] = "Unable to accept that friend request."
    else:
        # should never happen
        payload['response'] = "You must be authenticated to accept a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


def remove_friend(request, *args, **kwargs):
    user = request.user
    payload = {
    }

    if request.POST and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        user_id = int(user_id)
        if user_id:
            try:
                removee = Account.objects.get(pk=int(user_id))
                friend_list = FriendList.objects.get(user=user)
                # we will get our own friend list and then remove the another person from the list of our own . it will take one argument. the user who is getting remove from the friend list .
                friend_list.unfriend(removee)
                payload["response"] = "Sucessfully removed the friend !"
            except Exception as e:
                payload["response"] = "Something went wrong {}".format(str(e))
        else:
            payload["response"] = "There was an error "
    else:
        payload["responpse"] = "You must be authenticated to reomove the friend !!"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def decline_friend_request(request, friend_request_id, *args, **kwargs):
    user = request.user
    payload = {
    }
    if request.method == "GET" and user.is_authenticated:
        friend_request_id = int(friend_request_id)
        print('This is the friend request id ->', friend_request_id)
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if friend_request.receiver == user:
                if friend_request:
                    friend_request.decline()
                    payload["response"] = "Declined the request !"
                else:
                    payload["response"] = "Something went wrong !"
            else:
                payload["response"] = "This is not your friend request to accept !"
        else:
            payload["response"] = "There is no friend request to you"

    else:
        payload["response"] = "You must be authenticated to decline the request"
    return HttpResponse(json.dumps(payload), content_type="application/json")


def cancel_friend_request(request, *args, **kwargs):
    payload = {

    }
    user = request.user

    if user.is_authenticated and request.POST:
        account_id = int(request.POST.get("friend_request_id"))
        try:
            account = Account.objects.get(pk=account_id)
            if account:
                try:
                    friend_requests = FriendRequest.objects.filter(
                        sender=user, receiver=account, is_active=True)

                    for request in friend_requests:
                        print(request)
                        request.cancel()
                        print("Is cancelled !")
                        

                    payload["response"] = "Cancelled the request !"
                except Exception as e:
                    print(e)
                    payload["response"] = "No friend request there"
            else:
                payload["response"] = "There is no friend request for cancelling the request !"
        except Account.DoesNotExist:
            payload["response"] = "There is no account to cancel the request to !"
    else:
        payload["response"] = "You need to be authenticated to cancel the request , kindly login"

    return HttpResponse(json.dumps(payload), content_type="application/json")

