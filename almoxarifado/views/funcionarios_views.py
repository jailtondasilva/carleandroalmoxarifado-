"""
Views para gerenciamento de funcionários.

Inclui listagem, CRUD básico e geração de PDF via xhtml2pdf para exportar os
dados. As views realizam validação simples dos campos e retornam mensagens
ou redirecionamentos apropriados.
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404  # renderiza templates, redireciona e retorna erro 404 caso não encontre
from django.db.models import Q  # usado para filtros com OR/AND no banco de dados
from django.core.paginator import Paginator  # responsável pela paginação
from django.contrib.auth.decorators import login_required  # usado para restringir acesso a usuários logados
from ..models import Funcionario, Instituicao  # importando os modelos do app

# ====================================================================
# LISTAR FUNCIONÁRIOS
# ====================================================================
def lista_funcionarios(request):
    """
    Lista funcionários com busca por nome, e-mail ou telefone e paginação.
    """
    # Captura o termo de busca enviado via GET (ex: ?q=joao)
    q = request.GET.get('q', '').strip()

    # Busca todos os funcionários já trazendo a instituição relacionada (otimização do banco)
    funcionarios = Funcionario.objects.select_related('instituicao').all()

    # Se houver termo de busca, filtra pelo nome, email ou telefone (case insensitive)
    if q:
        funcionarios = funcionarios.filter(
            Q(nome__icontains=q) |
            Q(email__icontains=q) |
            Q(telefone__icontains=q)
        )

    # Cria a paginação (10 funcionários por página)
    paginator = Paginator(funcionarios, 10)
    page_number = request.GET.get('page')  # pega o número da página atual
    page_obj = paginator.get_page(page_number)  # retorna a página pedida

    # Retorna para o template com os dados
    return render(
        request,
        'funcionario/lista.html',
        {'page_obj': page_obj, 'q': q}
    )

# ====================================================================
# CADASTRAR FUNCIONÁRIOS
# ====================================================================
def cadastrar_funcionarios(request):
    """
    Cadastra um novo funcionário no sistema.
    """
    erros = {}  # dicionário para guardar erros de validação
    val = {}    # dicionário para manter valores preenchidos (caso dê erro e precise reexibir no form)

    # Quando o formulário for enviado (POST)
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        data_nascimento = request.POST.get('data_nascimento', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        instituicao_id = request.POST.get('instituicao', '').strip()

        # Guarda os valores já digitados para não perder no caso de erro
        val = {
            'nome': nome,
            'data_nascimento': data_nascimento,
            'email': email,
            'telefone': telefone,
            'instituicao': instituicao_id,
        }

        # Validações simples
        if not nome:
            erros['nome'] = 'Nome é obrigatório.'
        if not email:
            erros['email'] = 'E-mail é obrigatório.'
        if not instituicao_id:
            erros['instituicao'] = 'Instituição é obrigatória.'

        # Se não houver erros, salva no banco
        if not erros:
            # Busca a instituição pelo ID
            instituicao = get_object_or_404(Instituicao, pk=instituicao_id)

            # Cria o funcionário
            Funcionario.objects.create(
                nome=nome,
                data_nascimento=data_nascimento,
                email=email,
                telefone=telefone,
                instituicao=instituicao
                # O campo 'user' não é preenchido aqui
            )
            return redirect('lista_funcionarios')  # redireciona após salvar

    # Se não for POST ou se houver erro, recarrega o formulário
    instituicoes = Instituicao.objects.all()
    return render(
        request,
        'funcionario/cadastrar.html',
        {'erros': erros, 'val': val, 'instituicoes': instituicoes}
    )

# ====================================================================
# EDITAR FUNCIONÁRIOS
# ====================================================================
def editar_funcionarios(request, pk):
    """
    Edita os dados de um funcionário.
    """
    # Busca o funcionário pelo ID (pk). Se não existir -> 404
    funcionario = get_object_or_404(Funcionario, pk=pk)

    # Dicionários para erros e valores iniciais
    erros = {}
    val = {
        'nome': funcionario.nome,
        'data_nascimento': funcionario.data_nascimento,
        'email': funcionario.email,
        'telefone': funcionario.telefone,
        'instituicao': funcionario.instituicao.id if funcionario.instituicao else '',
    }

    # Quando o formulário for enviado (POST)
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        data_nascimento = request.POST.get('data_nascimento', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        instituicao_id = request.POST.get('instituicao', '').strip()

        # Atualiza os valores para manter no form em caso de erro
        val.update({
            'nome': nome,
            'data_nascimento': data_nascimento,
            'email': email,
            'telefone': telefone,
            'instituicao': instituicao_id,
        })

        # Validações
        if not nome:
            erros['nome'] = 'Nome é obrigatório.'
        if not email:
            erros['email'] = 'E-mail é obrigatório.'
        if not instituicao_id:
            erros['instituicao'] = 'Instituição é obrigatória.'

        # Se não houver erros, atualiza no banco
        if not erros:
            funcionario.nome = nome
            funcionario.data_nascimento = data_nascimento
            funcionario.email = email
            funcionario.telefone = telefone
            funcionario.instituicao = get_object_or_404(Instituicao, pk=instituicao_id)
            funcionario.save()  # salva alterações
            return redirect('lista_funcionarios')

    # Renderiza o formulário de edição
    instituicoes = Instituicao.objects.all()
    return render(
        request,
        'funcionario/editar.html',
        {'funcionario': funcionario, 'erros': erros, 'val': val, 'instituicoes': instituicoes}
    )

# ====================================================================
# EXCLUIR FUNCIONÁRIOS
# ====================================================================
def excluir_funcionarios(request, pk):
    """
    Exclui um funcionário.
    """
    funcionario = get_object_or_404(Funcionario, pk=pk)

    # Se for POST, confirma a exclusão
    if request.method == 'POST':
        funcionario.delete()
    return redirect('lista_funcionarios')




def funcionarios_pdf(request):
    """
    Gera e retorna um PDF com os dados de todos os funcionários usando um template HTML.
    """
    # Busca todos os funcionários do banco
    funcionarios = Funcionario.objects.all()

    # Caminho do template HTML usado para gerar o PDF
    template_path = 'funcionario/pdf.html'

    # Contexto enviado para o template
    context = {'funcionarios': funcionarios}

    # Renderiza o HTML em string
    html = render_to_string(template_path, context)

    # Configuração da resposta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="funcionarios.pdf"'

    # Gera o PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Verifica se houve erro
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)

    return response

