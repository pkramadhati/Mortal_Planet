from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    pass
    def __str__(self):
        return self.username


class Category(models.Model):

    class Meta:
        verbose_name_plural = "categories"
    name = models.CharField(max_length=255)
    share = models.BooleanField(default=True)
   
    def __str__(self):
        return self.name


class Location(models.Model):

    class Meta:
        verbose_name_plural = "locations"
    area = models.CharField(max_length=255)
   
    def __str__(self):
        return self.area

class Post(models.Model):
    open = models.BooleanField(default=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, blank=True, null=True)
    location = models.ForeignKey("Location",on_delete=models.SET_NULL, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='PostImages',null=True,blank=True)
    poster = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)

class Comment(models.Model):
    content = models.TextField(blank=True)
    commenter = models.ForeignKey("User", on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return self.content   

class Message(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("User", on_delete=models.PROTECT, related_name="messages_sent")
    recipients = models.ManyToManyField("User", related_name="messages_received")
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.username,
            "recipients": [user.username for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p"),
            "read": self.read,
        }
