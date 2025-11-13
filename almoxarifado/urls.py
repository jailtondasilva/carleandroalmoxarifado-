from django.urls import path
from .views import instituicao_views, funcionarios_views, produtos_views, movimentacao_views, dashboard_views


urlpatterns = [
    # DASHBOARD
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    path('relatorio-estoque/', dashboard_views.relatorio_estoque, name='relatorio_estoque'),
    path('relatorio-movimentacoes/', dashboard_views.relatorio_movimentacoes, name='relatorio_movimentacoes'),
    path('estoque-baixo/', dashboard_views.produtos_estoque_baixo, name='estoque_baixo'),

    # INSTITUIÇÕES
    path('instituicoes/', instituicao_views.lista_instituicoes, name='lista_instituicoes'),
    path('menu/', instituicao_views.menu, name='menu_area'),
    path('instituicoes/cadastrar/', instituicao_views.cadastrar_instituicoes, name='cadastrar_instituicoes'),
    path('instituicoes/editar/<int:pk>/', instituicao_views.editar_instituicoes, name='editar_instituicao'),
    path('instituicoes/excluir/<int:pk>/', instituicao_views.excluir_instituicao, name='excluir_instituicao'),
    path('instituicoes/pdf/', instituicao_views.instituicao_pdf, name='instituicao_pdf'),

    # FUNCIONÁRIOS
    path('funcionarios/', funcionarios_views.lista_funcionarios, name='lista_funcionarios'),
    path('funcionarios/cadastrar/', funcionarios_views.cadastrar_funcionarios, name='cadastrar_funcionarios'),
    path('funcionarios/editar/<int:pk>/', funcionarios_views.editar_funcionarios, name='editar_funcionarios'),
    path('funcionarios/excluir/<int:pk>/', funcionarios_views.excluir_funcionarios, name='excluir_funcionarios'),
    path('funcionarios/pdf/', funcionarios_views.funcionarios_pdf, name='funcionarios_pdf'),

    # PRODUTOS
    path('produtos/', produtos_views.lista_produtos, name='lista_produtos'),
    path('produtos/cadastrar/', produtos_views.cadastrar_produto, name='cadastrar_produto'),
    path('produtos/editar/<int:id>/', produtos_views.editar_produto, name='editar_produto'),
    path('produtos/deletar/<int:id>/', produtos_views.deletar_produto, name='deletar_produto'),

    # MOVIMENTAÇÕES
    path('movimentacoes/', movimentacao_views.lista_movimentacoes, name='lista_movimentacoes'),
    path('movimentacoes/entrada/', movimentacao_views.registrar_entrada, name='registrar_entrada'),
    path('movimentacoes/saida/', movimentacao_views.registrar_saida, name='registrar_saida'),
    path('movimentacoes/<int:id>/', movimentacao_views.detalhes_movimentacao, name='detalhes_movimentacao'),

    # AUTENTICAÇÃO
    path('login/', instituicao_views.login_instituicoes, name='login_instituicoes'),
    path('logout/', instituicao_views.logout_instituicoes, name='logout_instituicoes'),
    path('area-instituicao/', instituicao_views.area_instituicoes, name='area_instituicao'),
    path('', instituicao_views.area_instituicoes, name='area_instituicoes'),
]

