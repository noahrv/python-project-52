from django.urls import path
from core import views
from core.views import HomeView


urlpatterns = [
    path('', views.home, name='home'),
    path('', HomeView.as_view(), name='home'),
]