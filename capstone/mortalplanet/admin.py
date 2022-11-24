from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Category,Location,Post,Comment,Message

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Message)
