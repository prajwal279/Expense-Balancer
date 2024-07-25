from django.contrib import admin
from django.urls import path
from expenses import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.SignupPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('home/',views.HomePage,name='home'),
    path('logout/',views.LogoutPage,name='logout'),
    path('groups/create/', views.create_group, name='create_group'),    
    path('groups/delete/<int:group_id>/', views.delete_group, name='delete_group'),
    path('groups/edit/<int:group_id>/', views.edit_group, name='edit_group'),
    path('friends/add/', views.add_friend, name='add_friend'),
    path('friends/', views.friend_list, name='friend_list'),
]
