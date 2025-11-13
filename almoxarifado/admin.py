"""
Configurações do Django Admin para os modelos do app `almoxarifado`.

Aqui definimos como os modelos aparecem no painel admin (colunas na
lista, filtros e campos somente leitura). Comentários explicam a
finalidade de cada configuração principal.
"""

from django.contrib import admin
from .models import Instituicao, Funcionario, Categoria, Produto, Movimentacao


@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    # Colunas exibidas na listagem do admin
    list_display = ('nome', 'cnpj', 'cidade', 'ativo', 'data_criacao')
    # Filtros laterais úteis para navegação rápida
    list_filter = ('ativo', 'estado', 'data_criacao')
    # Campos pesquisáveis pelo campo de busca do admin
    search_fields = ('nome', 'cnpj', 'cidade')
    # Campos que não devem ser editados manualmente no admin
    readonly_fields = ('data_criacao',)


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'instituicao', 'telefone', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'instituicao', 'data_criacao')
    search_fields = ('nome', 'email', 'telefone')
    readonly_fields = ('data_criacao',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome',)
    readonly_fields = ('data_criacao',)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'categoria', 'quantidade_atual', 'quantidade_minima', 'preco_unitario', 'ativo')
    list_filter = ('ativo', 'categoria', 'instituicao', 'data_criacao')
    search_fields = ('codigo', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    # Organização dos campos no formulário de edição do admin
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'nome', 'descricao', 'categoria', 'instituicao')
        }),
        ('Estoque', {
            'fields': ('quantidade_atual', 'quantidade_minima', 'preco_unitario')
        }),
        ('Status', {
            'fields': ('ativo', 'data_criacao', 'data_atualizacao')
        }),
    )


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'tipo', 'quantidade', 'funcionario', 'data_movimentacao')
    list_filter = ('tipo', 'data_movimentacao', 'produto__instituicao')
    search_fields = ('produto__nome', 'motivo', 'funcionario__nome')
    readonly_fields = ('data_movimentacao',)
    # Permite navegação por data no topo da listagem
    date_hierarchy = 'data_movimentacao'
