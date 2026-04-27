from django.contrib import admin
from .models import * #importa nossos models
#adiciona a interface do adm
# Register your models here.
class FabricanteAdmin(admin.ModelAdmin):
    # Cria um filtro de hierarquia com datas
    date_hierarchy = 'criado_em'
class ProdutoAdmin(admin.ModelAdmin):
    date_hierarchy = 'criado_em'
    list_display = ('Produto', 'destaque', 'promocao', 'msgPromocao','preco', 'categoria',)
    empty_value_display = 'Vazio'
admin.site.register(Fabricante,FabricanteAdmin)
admin.site.register(Categoria)
admin.site.register(Produto, ProdutoAdmin)
