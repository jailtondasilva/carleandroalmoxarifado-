"""
Views para gerenciamento de movimentações do almoxarifado.

Contém listagem, registro de entradas/saídas, detalhes e validações
simples. As operações que alteram o estoque utilizam `transaction.atomic`
para garantir consistência entre `Movimentacao` e `Produto`.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import transaction
from ..models import Movimentacao, Produto, Funcionario


# ====================================================================
# LISTAR MOVIMENTAÇÕES
# ====================================================================
@login_required(login_url='login_instituicoes')
def lista_movimentacoes(request):
    """Lista todas as movimentações com filtros por tipo e produto.

    - `q`: busca por nome/código do produto ou pelo motivo.
    - `tipo`: filtra por tipo (entrada/saida/ajuste).
    Os resultados são paginados para evitar retorno excessivo.
    """
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()

    movimentacoes = Movimentacao.objects.select_related('produto', 'funcionario').all()

    if q:
        movimentacoes = movimentacoes.filter(
            Q(produto__nome__icontains=q) |
            Q(produto__codigo__icontains=q) |
            Q(motivo__icontains=q)
        )

    if tipo:
        movimentacoes = movimentacoes.filter(tipo=tipo)

    paginator = Paginator(movimentacoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tipos = Movimentacao.TIPO_CHOICES

    return render(
        request,
        'movimentacao/lista.html',
        {
            'page_obj': page_obj,
            'tipos': tipos,
            'q': q,
            'tipo': tipo
        }
    )


# ====================================================================
# REGISTRAR ENTRADA
# ====================================================================
@login_required(login_url='login_instituicoes')
def registrar_entrada(request):
    """Registra uma entrada de produto no estoque.

    Validações básicas garantem que o produto exista, que a
    quantidade seja um número inteiro positivo e que o motivo seja
    informado. A movimentação é salva dentro de uma transação.
    """
    erros = {}
    val = {}

    if request.method == 'POST':
        produto_id = request.POST.get('produto', '').strip()
        quantidade = request.POST.get('quantidade', '0').strip()
        motivo = request.POST.get('motivo', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()

        val = {
            'produto': produto_id,
            'quantidade': quantidade,
            'motivo': motivo,
            'observacoes': observacoes,
        }

        # Validações
        if not produto_id:
            erros['produto'] = 'Produto é obrigatório.'

        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                erros['quantidade'] = 'Quantidade deve ser maior que zero.'
        except ValueError:
            erros['quantidade'] = 'Quantidade deve ser um número.'
            quantidade = 0

        if not motivo:
            erros['motivo'] = 'Motivo é obrigatório.'

        if not erros:
            try:
                produto = Produto.objects.get(pk=produto_id)
                funcionario = None

                try:
                    funcionario = Funcionario.objects.first()
                except Funcionario.DoesNotExist:
                    pass

                with transaction.atomic():
                    movimentacao = Movimentacao(
                        produto=produto,
                        tipo='entrada',
                        quantidade=quantidade,
                        motivo=motivo,
                        observacoes=observacoes,
                        funcionario=funcionario
                    )
                    movimentacao.salvar_e_atualizar_estoque()

                messages.success(request, f'Entrada de {quantidade} unidade(s) de "{produto.nome}" registrada!')
                return redirect('lista_movimentacoes')

            except Produto.DoesNotExist:
                erros['produto'] = 'Produto não encontrado.'

    produtos = Produto.objects.filter(ativo=True).select_related('categoria')

    return render(
        request,
        'movimentacao/entrada.html',
        {
            'produtos': produtos,
            'erros': erros,
            'val': val
        }
    )


# ====================================================================
# REGISTRAR SAÍDA
# ====================================================================
@login_required(login_url='login_instituicoes')
def registrar_saida(request):
    """Registra uma saída de produto do estoque.

    Antes de criar a movimentação verifica se há estoque suficiente
    para evitar inconsistências. Em caso de estoque insuficiente, a
    view retorna mensagem de erro para o usuário.
    """
    erros = {}
    val = {}

    if request.method == 'POST':
        produto_id = request.POST.get('produto', '').strip()
        quantidade = request.POST.get('quantidade', '0').strip()
        motivo = request.POST.get('motivo', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()

        val = {
            'produto': produto_id,
            'quantidade': quantidade,
            'motivo': motivo,
            'observacoes': observacoes,
        }

        # Validações
        if not produto_id:
            erros['produto'] = 'Produto é obrigatório.'

        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                erros['quantidade'] = 'Quantidade deve ser maior que zero.'
        except ValueError:
            erros['quantidade'] = 'Quantidade deve ser um número.'
            quantidade = 0

        if not motivo:
            erros['motivo'] = 'Motivo é obrigatório.'

        if not erros:
            try:
                produto = Produto.objects.get(pk=produto_id)

                if produto.quantidade_atual < quantidade:
                    erros['quantidade'] = f'Estoque insuficiente. Disponível: {produto.quantidade_atual}'
                else:
                    funcionario = None
                    try:
                        funcionario = Funcionario.objects.first()
                    except Funcionario.DoesNotExist:
                        pass

                    with transaction.atomic():
                        movimentacao = Movimentacao(
                            produto=produto,
                            tipo='saida',
                            quantidade=quantidade,
                            motivo=motivo,
                            observacoes=observacoes,
                            funcionario=funcionario
                        )
                        movimentacao.salvar_e_atualizar_estoque()

                    messages.success(request, f'Saída de {quantidade} unidade(s) de "{produto.nome}" registrada!')
                    return redirect('lista_movimentacoes')

            except Produto.DoesNotExist:
                erros['produto'] = 'Produto não encontrado.'

    produtos = Produto.objects.filter(ativo=True).select_related('categoria')

    return render(
        request,
        'movimentacao/saida.html',
        {
            'produtos': produtos,
            'erros': erros,
            'val': val
        }
    )


# ====================================================================
# DETALHES DA MOVIMENTAÇÃO
# ====================================================================
@login_required(login_url='login_instituicoes')
def detalhes_movimentacao(request, id):
    """Exibe os detalhes de uma movimentação.

    Mostra produto, funcionário, tipo, quantidade, motivo e observações.
    """
    movimentacao = get_object_or_404(Movimentacao, pk=id)

    return render(
        request,
        'movimentacao/detalhes.html',
        {'movimentacao': movimentacao}
    )
