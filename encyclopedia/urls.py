from django.urls import path
from . import util

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.redirect, name="base"),
    path("wiki/", views.index, name="index"),
    path("wiki/new", views.new_wiki, name="new_wiki"),
    path("wiki/edit", views.edit_wiki_list, name="edit_wiki_list"),
    path("wiki/edit/<str:page_name>", views.edit_wiki, name="edit_wiki"),
    path("wiki/random", views.random_page, name="random_page"),
    path("search/", views.search, name="search"),
    path("wiki/<str:page_name>", views.render_page, name="render_page")
]

