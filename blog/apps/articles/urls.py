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
    path("tag/<slug:tag_slug>/", views.article_list, name="article_list_by_tag"),
    path("<slug:article_slug>/", views.article_detail, name="article_detail"),
]
