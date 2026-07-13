from django.shortcuts import render, redirect
from loja.models import Categoria


def list_categoria_view(request, id=None):
    categorias = Categoria.objects.all().order_by('-id')
    if id is not None:
        categorias = categorias.filter(id=id)
    return render(request, 'categoria/categoria.html', {'categorias': categorias}, status=200)


def create_categoria_view(request):
    if request.method == 'POST':
        nome = request.POST.get('Categoria')
        if nome:
            Categoria.objects.create(Categoria=nome)
        return redirect('/categoria')

    return render(request, 'categoria/categoria-create.html', status=200)


def edit_categoria_view(request, id=None):
    categoria = Categoria.objects.filter(id=id).first()
    return render(request, 'categoria/categoria-edit.html', {'categoria': categoria}, status=200)


def edit_categoria_postback(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nome = request.POST.get('Categoria')
        obj = Categoria.objects.filter(id=id).first()
        if obj and nome is not None:
            obj.Categoria = nome
            obj.save()
    return redirect('/categoria')


def delete_categoria_view(request, id=None):
    categoria = Categoria.objects.filter(id=id).first()
    return render(request, 'categoria/categoria-delete.html', {'categoria': categoria}, status=200)


def delete_categoria_postback(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        obj = Categoria.objects.filter(id=id).first()
        if obj:
            obj.delete()
    return redirect('/categoria')
