from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.view_snapshots),
    path('register/', views.register_view),
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', views.logout_view),
    path('post/', views.make_post),
    path('comment/', views.make_comment),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)