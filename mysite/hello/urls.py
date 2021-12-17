from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.view_follower_snapshots),
    path('global/', views.view_global_snapshots),
    path('user/<str:username>/followers', views.view_user_followers),
    path('user/<str:username>/following', views.view_user_following),
    path('user/<str:username>', views.view_user),
    path('follow/<str:username>', views.follow_user),
    path('make_post/', views.make_post),
    path('make_comment/<int:post_id>', views.make_comment),
    path('like_post/<int:post_id>', views.like_post),
    path('post/<int:post_id>', views.view_post),
    path('likes/<int:post_id>', views.view_post_likes),
    path('register/', views.register_view),
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', views.logout_view),
    path('chat/', views.chat_view),
    path('chat/<str:room_name>/', views.view_room, name='room'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)