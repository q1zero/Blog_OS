from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path(
        "category/<slug:category_slug>/",
        views.article_list,
        name="article_list_by_category",
    ),
    path("tag/<int:tag_id>/", views.article_list, name="article_list_by_tag"),
    path("create/", views.article_create, name="article_create"),
    path("update/<slug:article_slug>/", views.article_update, name="article_update"),
    path("delete/<slug:article_slug>/", views.article_delete, name="article_delete"),
    path("like/<slug:article_slug>/", views.toggle_like, name="toggle_like"),
    path(
        "favorite/<slug:article_slug>/", views.toggle_favorite, name="toggle_favorite"
    ),
    path("<slug:article_slug>/", views.article_detail, name="article_detail"),
]
