"""
URL configuration for diploma_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from rest_framework.routers import DefaultRouter

from app.views import (UsersViewSet, FilesViewSet, get_link_for_file, retrieve_by_link, get_users,
                       get_user_files, get_mycloud_user, check_session, download_file, login_view, logout_view)


router = DefaultRouter()

router.register("api/users", UsersViewSet)
router.register("api/files", FilesViewSet)

urlpatterns = [
    path("api/get_link_for_file/", get_link_for_file),
    path("api/retrieve_by_link/", retrieve_by_link),
    path("api/login/", login_view),
    path("api/logout/", logout_view),
    path("api/get_mycloud_user/", get_mycloud_user),
    path("api/check_session/", check_session),
    path("api/get_user_files/", get_user_files),
    path("api/get_users/", get_users),
    path("api/download_file/", download_file),
    path("api/users/", UsersViewSet.as_view({
        'post': 'create',
        'patch': 'update',
        'delete': 'destroy'
    })),
    path('api/files/', FilesViewSet.as_view({
        'post': 'create',
        'patch': 'update',
        'delete': 'destroy'
    })),
] + router.urls

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
