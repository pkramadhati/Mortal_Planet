from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create, name="create"),
    path("share", views.share, name="share"),
    path("discover", views.discover, name="discover"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("post/<int:post_id>", views.post, name="post"),
    path("post/comment/<int:post_id>", views.comment, name="comment"),
    path("post/<int:post_id>/close", views.close, name="close"),
    path("engage", views.engage, name="engage"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
   

      # API Routes
    path("messages", views.compose, name="compose"),
    path("messages/<int:message_id>", views.message, name="message"),
    path("messages/<str:mailbox>", views.mailbox, name="mailbox"),
]
