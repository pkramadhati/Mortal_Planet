import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect, Http404,JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import User,Category,Location,Post,Comment,Message
from django.views.decorators.csrf import csrf_exempt
#Aspects of the code below is based on solutions to problem sets on CSCI-E-33




class CreatePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'image', 'category', 'location']

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

#Default View
def index(request):
    
    return render(request, "mortalplanet/index.html", {

    })



#User Registration  
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "mortalplanet/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password,first_name=first_name,last_name=last_name)
            user.save()
        except IntegrityError:
            return render(request, "mortalplanet/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mortalplanet/register.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "mortalplanet/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "mortalplanet/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


#Share Posts View 

def share(request):
    
    post = Post.objects.filter(category__in=[1,2,3]).order_by("-creation_time")
    return render(request, "mortalplanet/share.html", {
        "categories":Category.objects.filter(share=True),
        "posts":post,
    })

#Enagage Posts View 
def engage(request):
    post = Post.objects.filter(category__in=[4,5,6]).order_by("-creation_time")
    return render(request, "mortalplanet/engage.html", {     
       "categories": Category.objects.filter(share=False),
       "posts":post,
    })

#Share Posts View 

def discover(request):
   
    return render(request, "mortalplanet/discover.html", {  
    })

#Filter Posts by category
def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if (category_id in [4,5,6]):
        categories=Category.objects.filter(share=False)
    else:
        categories=Category.objects.filter(share=True)

    post = Post.objects.filter(category=category).order_by("-creation_time").all()
    return render(request, "mortalplanet/filteredPosts.html", {
        "posts": post,
        "categories": categories,
    })

#Comment on Posts
@login_required
def comment(request, post_id):
    if request.method == "POST":
        content = request.POST["comment"]
        post = get_object_or_404(Post, pk=post_id)
        comment = Comment(commenter=request.user, content=content, post=post)
        comment.save()
        return HttpResponseRedirect(reverse("post", args=(post.id,)))

#View Post 
def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "mortalplanet/post.html", {
        "post": post,
        "comments": post.comments.order_by("-creation_time").all(),
        })


#Close/Open Posts
@login_required
def close(request, post_id):
    if request.method =="POST":
        post = get_object_or_404(Post, pk=post_id)
        if post.open == True:
            if post.poster != request.user:
                return render(request, "mortalplanet/post.html", {
                "message": "You can only close a post that you created."
            })
            post.open = False
            post.save()
        else:
            post.open = True
            post.save()
    return HttpResponseRedirect(reverse("post", args=(post.id,)))


#Profile View
@login_required
def profile(request, user_id):
    post = Post.objects.filter(poster=request.user).order_by("-creation_time")
    return render(request, "mortalplanet/profile.html", {
        "myposts": post
    })


#Profile Posts View
@login_required
def profileposts(request, user_id):
    post = Post.objects.filter(poster=request.user).order_by("-creation_time")
    return render(request, "mortalplanet/profile.html", {
        "posts": post
    })


#Create a Post
@login_required
def create(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.poster = request.user
            post.save()
            return HttpResponseRedirect(reverse("share"))
        else:
            return render(request, "mortalplanet/create.html", {
                "form": form
            })
    else:
        return render(request, "mortalplanet/create.html", {
            "form": CreatePostForm()
        })


@login_required
def mailbox(request, mailbox):

    # Filter messages returned based on mailbox
    if mailbox == "inbox":
        messages = Message.objects.filter(
            user=request.user, recipients=request.user
        )
    elif mailbox == "sent":
        messages = Message.objects.filter(
            user=request.user, sender=request.user
        )
    
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return messages in reverse chronologial order
    messages = messages.order_by("-timestamp").all()
    return JsonResponse([message.serialize() for message in messages], safe=False)


@csrf_exempt
@login_required
def message(request, message_id):

    # Query for requested message
    try:
        message = Message.objects.get(user=request.user, pk=message_id)
    except message.DoesNotExist:
        return JsonResponse({"error": "message not found."}, status=404)

    # Return message contents
    if request.method == "GET":
        return JsonResponse(message.serialize())

    # Update whether message is read 
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            message.read = data["read"]
        message.save()
        return HttpResponse(status=204)

    # message must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


# Compose Messages 
@csrf_exempt
@login_required
def compose(request):
    
    # Composing a new message must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    print(f"resquest.body{request.body}")
    # Check recipient username
    data = json.loads(request.body)
    print(f"data{data}")
    users = [user.strip() for user in data.get("recipients").split(",")]


    recipients = []
    for user in users:
        try:
            user = User.objects.get(username=user)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with username {user} does not exist."
            }, status=400)


    # Get contents of message
    subject = data.get("subject", "")
    body = data.get("body", "")
    print(f"body{body}")

    # Create one message for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)

    for user in users:
        message = Message(
            user=user,
            sender=request.user,
            subject=subject,
            body=body,
            read=user == request.user
        )
        message.save()
        for recipient in recipients:
            message.recipients.add(recipient)
        message.save()

    return JsonResponse({"message": "Message sent successfully."}, status=201)

 