from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from ..models import Produto, Categoria, Instituicao, Movimentacao, Funcionario


"""
Views relacionadas a produtos.

As views usam `login_required` para proteger ações de CRUD, paginam
listas longas e validam entradas do usuário antes de persistir.
"""


# ====================================================================
# LISTAR PRODUTOS
# ====================================================================
@login_required(login_url='login_instituicoes')
def lista_produtos(request):
    """Lista produtos com busca por nome/código e filtro por categoria.

    - Consulta `q` para busca livre em nome/código.
    - `categoria` filtra por categoria ativa.
    - Os resultados são paginados para evitar carregamento excessivo.
    """
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()

    # Carrega relacionamentos que serão exibidos para evitar queries extras
    produtos = Produto.objects.select_related('categoria', 'instituicao').filter(ativo=True)

    if q:
        # Busca por nome ou código (case-insensitive)
        produtos = produtos.filter(
            Q(nome__icontains=q) |
            Q(codigo__icontains=q)
        )

    if categoria_id:
        # Valida entrada para evitar exceções
        try:
            produtos = produtos.filter(categoria_id=int(categoria_id))
        except (ValueError, TypeError):
            pass

    # Paginação padrão (15 por página)
    paginator = Paginator(produtos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.filter(ativo=True)

    return render(
        request,
        'produto/lista.html',
        {
            'page_obj': page_obj,
            'categorias': categorias,
            'q': q,
            'categoria_id': categoria_id
        }
    )


# ====================================================================
# CADASTRAR PRODUTO
# ====================================================================
@login_required(login_url='login_instituicoes')
def cadastrar_produto(request):
    """
    Cadastra um novo produto.
    """
    erros = {}
    val = {}

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        categoria_id = request.POST.get('categoria', '').strip()
        quantidade_minima = request.POST.get('quantidade_minima', '0').strip()
        preco_unitario = request.POST.get('preco_unitario', '0').strip()
        instituicao_id = request.POST.get('instituicao', '').strip()

        val = {
            'codigo': codigo,
            'nome': nome,
            'descricao': descricao,
            'categoria': categoria_id,
            'quantidade_minima': quantidade_minima,
            'preco_unitario': preco_unitario,
            'instituicao': instituicao_id,
        }

        # Validações
        if not codigo:
            erros['codigo'] = 'Código é obrigatório.'
        if not nome:
            erros['nome'] = 'Nome é obrigatório.'
        if not instituicao_id:
            erros['instituicao'] = 'Instituição é obrigatória.'

        try:
            quantidade_minima = int(quantidade_minima)
        except ValueError:
            erros['quantidade_minima'] = 'Quantidade mínima deve ser um número.'
            quantidade_minima = 0

        try:
            preco_unitario = float(preco_unitario)
        except ValueError:
            erros['preco_unitario'] = 'Preço deve ser um número.'
            preco_unitario = 0

        if not erros:
            try:
                instituicao = Instituicao.objects.get(pk=instituicao_id)
                categoria = None
                if categoria_id:
                    try:
                        categoria = Categoria.objects.get(pk=categoria_id)
                    except Categoria.DoesNotExist:
                        pass

                Produto.objects.create(
                    codigo=codigo,
                    nome=nome,
                    descricao=descricao,
                    categoria=categoria,
                    instituicao=instituicao,
                    quantidade_minima=quantidade_minima,
                    preco_unitario=preco_unitario
                )
                messages.success(request, f'Produto "{nome}" cadastrado com sucesso!')
                return redirect('lista_produtos')
            except Produto.DoesNotExist:
                erros['geral'] = 'Produto com este código já existe para esta instituição.'

    instituicoes = Instituicao.objects.filter(ativo=True)
    categorias = Categoria.objects.filter(ativo=True)

    return render(
        request,
        'produto/cadastrar.html',
        {
            'erros': erros,
            'val': val,
            'instituicoes': instituicoes,
            'categorias': categorias
        }
    )


# ====================================================================
# EDITAR PRODUTO
# ====================================================================
@login_required(login_url='login_instituicoes')
def editar_produto(request, id):
    """
    Edita um produto existente.
    """
    produto = get_object_or_404(Produto, pk=id)
    erros = {}

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        categoria_id = request.POST.get('categoria', '').strip()
        quantidade_minima = request.POST.get('quantidade_minima', '0').strip()
        preco_unitario = request.POST.get('preco_unitario', '0').strip()

        if not nome:
            erros['nome'] = 'Nome é obrigatório.'

        try:
            quantidade_minima = int(quantidade_minima)
        except ValueError:
            erros['quantidade_minima'] = 'Quantidade mínima deve ser um número.'

        try:
            preco_unitario = float(preco_unitario)
        except ValueError:
            erros['preco_unitario'] = 'Preço deve ser um número.'

        if not erros:
            produto.nome = nome
            produto.descricao = descricao
            produto.quantidade_minima = quantidade_minima
            produto.preco_unitario = preco_unitario

            if categoria_id:
                try:
                    produto.categoria = Categoria.objects.get(pk=categoria_id)
                except Categoria.DoesNotExist:
                    pass

            produto.save()
            messages.success(request, f'Produto "{nome}" atualizado com sucesso!')
            return redirect('lista_produtos')

    categorias = Categoria.objects.filter(ativo=True)

    return render(
        request,
        'produto/editar.html',
        {
            'produto': produto,
            'categorias': categorias,
            'erros': erros
        }
    )


# ====================================================================
# DELETAR PRODUTO
# ====================================================================
@login_required(login_url='login_instituicoes')
def deletar_produto(request, id):
    """
    Deleta um produto (soft delete - marca como inativo).
    """
    produto = get_object_or_404(Produto, pk=id)
    nome = produto.nome

    if request.method == 'POST':
        produto.ativo = False
        produto.save()
        messages.success(request, f'Produto "{nome}" removido com sucesso!')
        return redirect('lista_produtos')

    return render(
        request,
        'produto/deletar.html',
        {'produto': produto}
    )
