"""
URL configuration for tripmate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from planner import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('my_trips/', views.my_trips, name='my_trips'),
    path('plan_trip/', views.plan_trip, name='plan_trip'),
    path('explore_destination/', views.explore_destination, name='explore_destination'),
    path('recommend_trip/', views.recommend_trip, name='recommend_trip'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('user_details/', views.user_details, name='user_details'),
    path('trip_edit/<int:trip_id>/', views.trip_edit, name='trip_edit'),
    path('trip_delete/<int:trip_id>/', views.trip_delete, name='trip_delete'),
]
