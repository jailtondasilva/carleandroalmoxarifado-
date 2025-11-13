"""
Modelos principais do app `almoxarifado`.

Contém definições para Instituição, Funcionário, Categoria, Produto e
Movimentação. Os modelos incluem métodos utilitários (ex.: verificar
estoque baixo e atualizar estoque durante uma movimentação).

Observações de uso:
- `Produto.unique_together` garante código único por instituição.
- `Movimentacao.salvar_e_atualizar_estoque` aplica a lógica de negócio
    para entrada/saída/ajuste e salva tanto o produto quanto a movimentação.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Instituicao(models.Model):
    """Representa uma instituição/empresa que possui produtos no almoxarifado."""
    nome = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    telefone = models.CharField(max_length=20)
    cnpj = models.CharField(max_length=18, unique=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Funcionario(models.Model):
    """Dados básicos de um funcionário vinculado a uma instituição."""
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    """Categoria de produtos — usada para agrupar e filtrar produtos."""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """Modelo de produto com informações de estoque e preço."""
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    quantidade_minima = models.PositiveIntegerField(default=0)
    quantidade_atual = models.PositiveIntegerField(default=0)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['codigo', 'instituicao']
        ordering = ['nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def esta_com_estoque_baixo(self):
        """Retorna True se a quantidade atual for menor ou igual à mínima."""
        return self.quantidade_atual <= self.quantidade_minima


class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    motivo = models.TextField(blank=True)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True)
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_movimentacao']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome} ({self.quantidade})"

    def salvar_e_atualizar_estoque(self):
        """Aplica a movimentação no estoque e persiste ambos os objetos.

        - `entrada`: adiciona a quantidade ao estoque.
        - `saida`: subtrai se houver estoque suficiente; lança `ValueError`
          caso contrário.
        - `ajuste`: define o estoque para o valor informado (uso administrativo).

        Este método salva primeiro o `produto` e em seguida a própria
        `movimentacao` garantindo consistência do estoque.
        """
        if self.tipo == 'entrada':
            self.produto.quantidade_atual += self.quantidade
        elif self.tipo == 'saida':
            if self.produto.quantidade_atual >= self.quantidade:
                self.produto.quantidade_atual -= self.quantidade
            else:
                # Protege contra estoque negativo — chamador deve tratar a exceção
                raise ValueError("Quantidade insuficiente em estoque")
        elif self.tipo == 'ajuste':
            # Ajuste define explicitamente a quantidade atual
            self.produto.quantidade_atual = self.quantidade

        # Persiste alteração de estoque e a movimentação
        self.produto.save()
        self.save()


