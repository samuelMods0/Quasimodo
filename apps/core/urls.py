from django.urls import path
from . import views

urlpatterns = [
    path("styleguide/", views.styleguide, name="styleguide"),
]
