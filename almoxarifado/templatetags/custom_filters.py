"""
Templatetags customizados para os templates do almoxarifado.

Este módulo registra filtros que são usados nos templates Django. Mantemos
os filtros simples e robustos — retornando um valor seguro (0) quando a
entrada não é numérica em vez de quebrar o template.

Uso nos templates:
    {% load custom_filters %}
    {{ produto.quantidade_atual|multiply:produto.preco_unitario }}

"""
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiplica `value` por `arg`.

    Ambos os parâmetros são convertidos para float. Se a conversão falhar
    (valor inválido ou None), o filtro retorna 0 para evitar erros no
    template e permitir exibição segura.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        # Retorna 0 em caso de dados inválidos — facilita o uso em relatórios
        # sem necessidade de validação adicional no template.
        return 0
