"""
Views relacionadas às instituições e autenticação de usuários.

Contém login/logout, CRUD de instituições, geração de PDF e views de área.
As views de autenticação usam `authenticate`/`login`/`logout` do Django.
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404  # renderiza páginas HTML, redireciona e retorna 404 caso não encontre
from django.db.models import Q  # usado para buscas avançadas (OR, AND)
from django.core.paginator import Paginator  # usado para paginação 
from ..models import Instituicao  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.decorators import login_required


def login_instituicoes(request):
    """Autentica um usuário usando `username` e `password`.

    Em caso de sucesso redireciona para a `dashboard`. Em caso de
    falha, exibe mensagem de erro no template de login.
    """
    if request.method == 'POST':
        matricula = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=matricula, password=senha)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos'})
    return render(request, 'login.html')


def logout_instituicoes(request):
    """Encerra a sessão do usuário e redireciona para a tela de login."""
    logout(request)
    return redirect('login_instituicoes')


def lista_instituicoes(request):
    """Lista instituições com busca por nome ou CNPJ e paginação."""
    # Captura o termo de busca enviado por GET (ex: ?q=123)
    q = request.GET.get('q', '').strip()

    # Pega todas as instituições
    instituicoes = Instituicao.objects.all()

    # Se o usuário digitou algo na busca, filtra pelo nome ou CNPJ (case insensitive)
    if q:
        instituicoes = instituicoes.filter(Q(nome__icontains=q) | Q(cnpj__icontains=q))

    # Cria paginação (10 itens por página)
    paginator = Paginator(instituicoes, 10)
    page_number = request.GET.get('page')  # pega a página atual da URL
    page_obj = paginator.get_page(page_number)  # retorna a página correta

    # Renderiza o template de lista com os dados
    return render(
        request,
        'instituicao/lista.html',
        {'page_obj': page_obj, 'q': q}
    )

# ====================================================================
# CADASTRAR INSTITUIÇÃO
# ====================================================================
def cadastrar_instituicoes(request):
    """
    Cadastra uma nova instituição.
    """
    erros = {}  # dicionário para guardar mensagens de erro
    val = {}    # dicionário para guardar os valores preenchidos (caso precise reaparecer no form)

    if request.method == 'POST':  # Se o formulário foi enviado
        # Captura os dados enviados no formulário
        nome = request.POST.get('nome', '').strip()
        cep = request.POST.get('cep', '').strip()
        logradouro = request.POST.get('logradouro', '').strip()
        numero = request.POST.get('numero', '').strip()
        bairro = request.POST.get('bairro', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        cnpj = request.POST.get('cnpj', '').strip()

        # Salva os valores preenchidos para reaparecer em caso de erro
        val = locals()

        # Validações
        if not nome:
            erros['nome'] = 'Nome é obrigatório.'
        if not cnpj:
            erros['cnpj'] = 'CNPJ é obrigatório.'

        # Se não tiver erro, cria a instituição no banco
        if not erros:
            Instituicao.objects.create(
                nome=nome,
                cep=cep,
                logradouro=logradouro,
                numero=numero,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                telefone=telefone,
                cnpj=cnpj
            )
            return redirect('lista_instituicoes')  # Redireciona após salvar

    # Renderiza o formulário de cadastro
    return render(
        request,
        'instituicao/cadastrar.html',
        {'erros': erros, 'val': val}
    )

# ====================================================================
# EDITAR INSTITUIÇÃO
# ====================================================================
def editar_instituicoes(request, pk):
    """
    Edita os dados de uma instituição.
    """
    # Busca a instituição pelo ID (pk). Se não existir, gera erro 404
    instituicao = get_object_or_404(Instituicao, pk=pk)

    # Dicionários para erros e valores iniciais do form
    erros = {}
    val = {
        'nome': instituicao.nome,
        'cep': instituicao.cep,
        'logradouro': instituicao.logradouro,
        'numero': instituicao.numero,
        'bairro': instituicao.bairro,
        'cidade': instituicao.cidade,
        'estado': instituicao.estado,
        'telefone': instituicao.telefone,
        'cnpj': instituicao.cnpj,
    }

    if request.method == 'POST':  # Se o formulário foi enviado
        # Pega os dados enviados
        nome = request.POST.get('nome', '').strip()
        cep = request.POST.get('cep', '').strip()
        logradouro = request.POST.get('logradouro', '').strip()
        numero = request.POST.get('numero', '').strip()
        bairro = request.POST.get('bairro', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        cnpj = request.POST.get('cnpj', '').strip()

        # Atualiza os valores no dicionário para manter preenchido
        val.update(locals())

        # Validações
        if not nome:
            erros['nome'] = 'Nome é obrigatório.'
        if not cnpj:
            erros['cnpj'] = 'CNPJ é obrigatório.'

        # Se não tiver erro, atualiza no banco
        if not erros:
            instituicao.nome = nome
            instituicao.cep = cep
            instituicao.logradouro = logradouro
            instituicao.numero = numero
            instituicao.bairro = bairro
            instituicao.cidade = cidade
            instituicao.estado = estado
            instituicao.telefone = telefone
            instituicao.cnpj = cnpj
            instituicao.save()
            return redirect('lista_instituicoes')

    # Renderiza o formulário de edição
    return render(
        request,
        'instituicao/editar.html',
        {'instituicao': instituicao, 'erros': erros, 'val': val}
    )

# ====================================================================
# EXCLUIR INSTITUIÇÃO
# ====================================================================
def excluir_instituicao(request, pk):
    """
    Exclui uma instituição.
    """
    # Busca a instituição pelo ID
    instituicao = get_object_or_404(Instituicao, pk=pk)

    # Se for POST, confirma exclusão
    if request.method == 'POST':
        instituicao.delete()

    # Sempre redireciona para a lista após a ação
    return redirect('lista_instituicoes')


def menu(request):
    return render(request, 'instituicao/area_instituicao.html')





def instituicao_pdf(request):
    """
    Gera e retorna um PDF com os dados de todas as instituições usando um template HTML.
    """
    # Busca todas as instituições do banco
    instituicoes = Instituicao.objects.all()

    # Caminho do template HTML usado para gerar o PDF
    template_path = 'instituicao/pdf.html'

    # Contexto enviado para o template
    context = {'instituicoes': instituicoes}

    # Renderiza o HTML em string
    html = render_to_string(template_path, context)

    # Configuração da resposta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="instituicoes.pdf"'

    # Gera o PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Verifica se houve erro
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)

    return response

 
def area_instituicoes(request):
    return render(request, 'instituicao/area_instituicao.html')
