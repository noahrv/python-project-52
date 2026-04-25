from django.http import HttpResponse
from django.views.generic import TemplateView


def home(request):
    return HttpResponse("Hello, Hexlet!")


class HomeView(TemplateView):
    template_name = "core/home.html"