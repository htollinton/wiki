from django.urls import path
from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.get_page, name="title"),
    path("newpage/", views.new_page, name="newpage"),
    path("edit/", views.edit, name="edit"),
    path("rand/", views.rand, name="rand"),
    path("search/", views.search, name="search"),
]
