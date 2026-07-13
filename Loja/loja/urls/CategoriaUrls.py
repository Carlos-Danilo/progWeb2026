from django.urls import path
from loja.views.CategoriaView import (
    list_categoria_view,
    create_categoria_view,
    edit_categoria_view,
    edit_categoria_postback,
    delete_categoria_view,
    delete_categoria_postback,
)

urlpatterns = [
    path("", list_categoria_view, name='categoria'),
    path("<int:id>", list_categoria_view, name='categoria'),
    path("create", create_categoria_view, name='create_categoria'),
    path("edit/<int:id>", edit_categoria_view, name='edit_categoria'),
    path("edit", edit_categoria_postback, name='edit_categoria_postback'),
    path("delete/<int:id>", delete_categoria_view, name='delete_categoria'),
    path("delete", delete_categoria_postback, name='delete_categoria_postback'),
]
