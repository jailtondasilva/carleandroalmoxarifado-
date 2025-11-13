"""
Views para dashboard e relatórios do almoxarifado.

Esta coleção de views calcula estatísticas e fornece relatórios que
ajudam na tomada de decisão (estoque baixo, movimentações recentes,
valor total em estoque etc.). As consultas usam expressões `F()` para
calcular valores derivados no banco.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from ..models import Produto, Movimentacao, Funcionario, Instituicao


# ====================================================================
# DASHBOARD PRINCIPAL
# ====================================================================
@login_required(login_url='login_instituicoes')
def dashboard(request):
    """Dashboard com resumo do almoxarifado.

    Calcula métricas principais:
    - total de produtos ativos
    - quantidade de produtos com estoque abaixo do mínimo
    - movimentações recentes (últimos 7 dias)
    - valor total do estoque (quantidade * preço)
    - top produtos por movimentação
    """
    # Total de produtos
    total_produtos = Produto.objects.filter(ativo=True).count()

    # Produtos com estoque baixo
    produtos_estoque_baixo = Produto.objects.filter(
        ativo=True,
        quantidade_atual__lte=F('quantidade_minima')
    ).count()

    # Movimentações da última semana
    uma_semana_atras = timezone.now() - timedelta(days=7)
    movimentacoes_semana = Movimentacao.objects.filter(
        data_movimentacao__gte=uma_semana_atras
    ).count()

    # Valor total do estoque: soma de (quantidade_atual * preco_unitario)
    valor_total_estoque = Produto.objects.filter(ativo=True).aggregate(
        total=Sum(F('quantidade_atual') * F('preco_unitario'))
    )['total'] or 0

    # Top 5 produtos mais movimentados
    produtos_populares = Movimentacao.objects.values('produto__nome', 'produto__codigo').annotate(
        total_movimentacoes=Count('id')
    ).order_by('-total_movimentacoes')[:5]

    # Últimas movimentações
    ultimas_movimentacoes = Movimentacao.objects.select_related(
        'produto', 'funcionario'
    ).order_by('-data_movimentacao')[:10]

    # Resumo por tipo de movimentação
    entradas = Movimentacao.objects.filter(tipo='entrada').count()
    saidas = Movimentacao.objects.filter(tipo='saida').count()
    ajustes = Movimentacao.objects.filter(tipo='ajuste').count()

    context = {
        'total_produtos': total_produtos,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'movimentacoes_semana': movimentacoes_semana,
        'valor_total_estoque': valor_total_estoque,
        'produtos_populares': produtos_populares,
        'ultimas_movimentacoes': ultimas_movimentacoes,
        'entradas': entradas,
        'saidas': saidas,
        'ajustes': ajustes,
    }

    return render(request, 'dashboard.html', context)


# ====================================================================
# RELATÓRIO DE ESTOQUE
# ====================================================================
@login_required(login_url='login_instituicoes')
def relatorio_estoque(request):
    """Relatório completo de estoque com filtros por categoria e estoque baixo."""
    produtos = Produto.objects.filter(ativo=True).select_related('categoria', 'instituicao')

    # Filtros
    categoria = request.GET.get('categoria', '').strip()
    estoque_baixo = request.GET.get('estoque_baixo', '').strip()

    if categoria:
        produtos = produtos.filter(categoria_id=categoria)

    if estoque_baixo == 'sim':
        produtos = produtos.filter(quantidade_atual__lte=F('quantidade_minima'))

    # Estatísticas
    total_itens = produtos.aggregate(total=Sum('quantidade_atual'))['total'] or 0
    valor_total = produtos.aggregate(
        total=Sum(F('quantidade_atual') * F('preco_unitario'))
    )['total'] or 0

    context = {
        'produtos': produtos,
        'total_itens': total_itens,
        'valor_total': valor_total,
        'categoria': categoria,
        'estoque_baixo': estoque_baixo,
    }

    return render(request, 'relatorio_estoque.html', context)


# ====================================================================
# RELATÓRIO DE MOVIMENTAÇÕES
# ====================================================================
@login_required(login_url='login_instituicoes')
def relatorio_movimentacoes(request):
    """Relatório de movimentações com filtros por período e tipo."""
    from django.core.paginator import Paginator

    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    tipo = request.GET.get('tipo', '').strip()

    movimentacoes = Movimentacao.objects.select_related('produto', 'funcionario')

    # Filtragem por datas — usamos try/except para ignorar valores inválidos
    if data_inicio:
        try:
            movimentacoes = movimentacoes.filter(data_movimentacao__gte=data_inicio)
        except Exception:
            pass

    if data_fim:
        try:
            movimentacoes = movimentacoes.filter(data_movimentacao__lte=data_fim)
        except Exception:
            pass

    if tipo:
        movimentacoes = movimentacoes.filter(tipo=tipo)

    movimentacoes = movimentacoes.order_by('-data_movimentacao')

    # Paginação
    paginator = Paginator(movimentacoes, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Estatísticas
    total_entradas = movimentacoes.filter(tipo='entrada').count()
    total_saidas = movimentacoes.filter(tipo='saida').count()

    context = {
        'page_obj': page_obj,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo': tipo,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
    }

    return render(request, 'relatorio_movimentacoes.html', context)


# ====================================================================
# ALERTA DE ESTOQUE BAIXO
# ====================================================================
@login_required(login_url='login_instituicoes')
def produtos_estoque_baixo(request):
    """Lista produtos com estoque abaixo do mínimo para ação imediata."""
    produtos = Produto.objects.filter(
        ativo=True,
        quantidade_atual__lte=F('quantidade_minima')
    ).select_related('categoria', 'instituicao').order_by('quantidade_atual')

    context = {
        'produtos': produtos,
        'total': produtos.count(),
    }

    return render(request, 'alerta_estoque_baixo.html', context)
