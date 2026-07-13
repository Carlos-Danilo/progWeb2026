from django.shortcuts import render, redirect
from loja.models import Fabricante


def list_fabricante_view(request, id=None):
    fabricantes = Fabricante.objects.all().order_by('-id')
    if id is not None:
        fabricantes = fabricantes.filter(id=id)
    return render(request, 'fabricante/fabricante.html', {'fabricantes': fabricantes}, status=200)


def create_fabricante_view(request):
    if request.method == 'POST':
        nome = request.POST.get('Fabricante')
        if nome:
            Fabricante.objects.create(Fabricante=nome)
        return redirect('/fabricante')

    return render(request, 'fabricante/fabricante-form.html', {
        'form_action': '/fabricante/create',
        'submit_label': 'Inserir',
        'title': 'Novo Fabricante',
        'fabricante': None
    }, status=200)


def edit_fabricante_view(request, id=None):
    fabricante = Fabricante.objects.filter(id=id).first()
    if request.method == 'POST':
        nome = request.POST.get('Fabricante')
        if fabricante and nome is not None:
            fabricante.Fabricante = nome
            fabricante.save()
        return redirect('/fabricante')

    return render(request, 'fabricante/fabricante-form.html', {
        'form_action': f'/fabricante/edit/{id}',
        'submit_label': 'Salvar',
        'title': 'Editar Fabricante',
        'fabricante': fabricante
    }, status=200)


def delete_fabricante_view(request, id=None):
    fabricante = Fabricante.objects.filter(id=id).first()
    return render(request, 'fabricante/fabricante-delete.html', {'fabricante': fabricante}, status=200)


def delete_fabricante_postback(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        obj = Fabricante.objects.filter(id=id).first()
        if obj:
            obj.delete()
    return redirect('/fabricante')
