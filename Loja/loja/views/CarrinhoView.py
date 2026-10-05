from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from loja.models import Carrinho, CarrinhoItem, Favorito, Produto


def create_carrinhoitem_view(request, produto_id=None):
    produto = get_object_or_404(Produto, pk=produto_id)
    carrinho_id = request.session.get('carrinho_id')
    carrinho = Carrinho.objects.filter(
        pk=carrinho_id,
        situacao=0,
    ).first()

    if (
        carrinho is None
        or timezone.localtime(carrinho.criado_em).date() != timezone.localdate()
    ):
        carrinho = Carrinho.objects.create()
        request.session['carrinho_id'] = carrinho.id

    item = CarrinhoItem.objects.filter(
        carrinho=carrinho,
        produto=produto,
    ).first()
    if item is None:
        CarrinhoItem.objects.create(
            carrinho=carrinho,
            produto=produto,
            quantidade=1,
            preco=produto.preco,
        )
    else:
        item.quantidade += 1
        item.save(update_fields=['quantidade'])

    return redirect('list_carrinho')


def list_carrinho_view(request):
    carrinho_id = request.session.get('carrinho_id')
    carrinho = Carrinho.objects.filter(pk=carrinho_id).first()
    itens = (
        carrinho.itens.select_related('produto').all()
        if carrinho is not None
        else CarrinhoItem.objects.none()
    )
    return render(
        request,
        'carrinho/carrinho-listar.html',
        {'carrinho': carrinho, 'itens': itens},
    )


@login_required
def confirmar_carrinho_view(request):
    carrinho_id = request.session.get('carrinho_id')
    carrinho = Carrinho.objects.filter(
        pk=carrinho_id,
        situacao=0,
    ).first()

    if carrinho is not None and carrinho.itens.exists():
        carrinho.user = request.user
        carrinho.situacao = 1
        carrinho.confirmado_em = timezone.now()
        carrinho.save(update_fields=['user', 'situacao', 'confirmado_em'])
        request.session.pop('carrinho_id', None)

    itens = (
        carrinho.itens.select_related('produto').all()
        if carrinho is not None
        else CarrinhoItem.objects.none()
    )
    return render(
        request,
        'carrinho/carrinho-confirmado.html',
        {'carrinho': carrinho, 'itens': itens},
    )


@require_POST
def remover_item_view(request, item_id):
    carrinho_id = request.session.get('carrinho_id')
    item = get_object_or_404(
        CarrinhoItem,
        pk=item_id,
        carrinho_id=carrinho_id,
        carrinho__situacao=0,
    )
    item.delete()
    return redirect('list_carrinho')


@require_POST
def aumentar_quantidade_view(request, item_id):
    item = get_object_or_404(
        CarrinhoItem,
        pk=item_id,
        carrinho_id=request.session.get('carrinho_id'),
        carrinho__situacao=0,
    )
    item.quantidade += 1
    item.save(update_fields=['quantidade'])
    return redirect('list_carrinho')


@require_POST
def diminuir_quantidade_view(request, item_id):
    item = get_object_or_404(
        CarrinhoItem,
        pk=item_id,
        carrinho_id=request.session.get('carrinho_id'),
        carrinho__situacao=0,
    )
    if item.quantidade > 1:
        item.quantidade -= 1
        item.save(update_fields=['quantidade'])
    return redirect('list_carrinho')


@login_required
def favoritar_produto_view(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    if request.method == 'POST':
        Favorito.objects.get_or_create(user=request.user, produto=produto)
        return redirect('favoritos')
    return render(
        request,
        'favoritos/favoritar-confirmacao.html',
        {'produto': produto},
    )


@login_required
@require_POST
def remover_favorito_view(request, produto_id):
    favorito = get_object_or_404(
        Favorito,
        user=request.user,
        produto_id=produto_id,
    )
    favorito.delete()
    return redirect('favoritos')


@login_required
def list_favoritos_view(request):
    favoritos = (
        Favorito.objects.filter(user=request.user)
        .select_related('produto')
        .order_by('-criado_em')
    )
    return render(request, 'favoritos/favoritos-listar.html', {'favoritos': favoritos})
