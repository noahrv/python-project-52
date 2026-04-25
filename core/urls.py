from django.urls import path
from .views import (
    UserListView, UserCreateView, UserUpdateView, UserDeleteView,
    UserLoginView, UserLogoutView, HomeView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]