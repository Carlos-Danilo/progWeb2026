from django.urls import path

from loja.views.CarrinhoView import (
    aumentar_quantidade_view,
    confirmar_carrinho_view,
    create_carrinhoitem_view,
    diminuir_quantidade_view,
    favoritar_produto_view,
    list_favoritos_view,
    list_carrinho_view,
    remover_favorito_view,
    remover_item_view,
)


urlpatterns = [
    path('', list_carrinho_view, name='list_carrinho'),
    path('<int:produto_id>', create_carrinhoitem_view, name='create_carrinhoitem'),
    path('confirmar', confirmar_carrinho_view, name='confirmar_carrinho'),
    path('item/<int:item_id>/aumentar', aumentar_quantidade_view, name='aumentar_carrinhoitem'),
    path('item/<int:item_id>/diminuir', diminuir_quantidade_view, name='diminuir_carrinhoitem'),
    path('remover/<int:item_id>/', remover_item_view, name='remover_carrinhoitem'),
    path('favoritos/', list_favoritos_view, name='favoritos'),
    path('favoritos/adicionar/<int:produto_id>/', favoritar_produto_view, name='favoritar_produto'),
    path('favoritos/remover/<int:produto_id>/', remover_favorito_view, name='remover_favorito'),
]
