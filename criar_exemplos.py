import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from almoxarifado.models import Instituicao, Funcionario, Categoria, Produto, Movimentacao
from datetime import datetime, timedelta

print("\n" + "=" * 80)
print("CRIANDO DADOS DE EXEMPLO")
print("=" * 80)

# Limpar dados existentes (opcional - descomente se quiser)
# Instituicao.objects.all().delete()
# Funcionario.objects.all().delete()
# Categoria.objects.all().delete()
# Produto.objects.all().delete()
# Movimentacao.objects.all().delete()

# 1. Criar Instituições
print("\n📦 Criando Instituições...")
inst1, created1 = Instituicao.objects.get_or_create(
    cnpj='11.222.333/0001-81',
    defaults={
        'nome': 'Hospital Central de São Paulo',
        'cep': '01310-100',
        'logradouro': 'Avenida Paulista',
        'numero': '1578',
        'bairro': 'Bela Vista',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'telefone': '(11) 3149-2000',
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created1 else '⚠️  Já existe'}: {inst1.nome}")

inst2, created2 = Instituicao.objects.get_or_create(
    cnpj='44.555.666/0001-99',
    defaults={
        'nome': 'Clínica Médica do Rio de Janeiro',
        'cep': '20040-020',
        'logradouro': 'Avenida Rio Branco',
        'numero': '1',
        'bairro': 'Centro',
        'cidade': 'Rio de Janeiro',
        'estado': 'RJ',
        'telefone': '(21) 2533-9000',
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created2 else '⚠️  Já existe'}: {inst2.nome}")

# 2. Criar Funcionários
print("\n👥 Criando Funcionários...")
func1, created3 = Funcionario.objects.get_or_create(
    email='maria.silva@hospital.com',
    defaults={
        'nome': 'Maria Silva Santos',
        'data_nascimento': '1990-05-15',
        'telefone': '(11) 98765-4321',
        'instituicao': inst1,
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created3 else '⚠️  Já existe'}: {func1.nome}")

func2, created4 = Funcionario.objects.get_or_create(
    email='carlos.oliveira@clinica.com',
    defaults={
        'nome': 'Carlos Oliveira Costa',
        'data_nascimento': '1988-10-22',
        'telefone': '(21) 99876-5432',
        'instituicao': inst2,
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created4 else '⚠️  Já existe'}: {func2.nome}")

# 3. Criar Categorias
print("\n📂 Criando Categorias...")
cat1, created5 = Categoria.objects.get_or_create(
    nome='Medicamentos',
    defaults={
        'descricao': 'Medicamentos diversos e farmacêuticos',
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created5 else '⚠️  Já existe'}: {cat1.nome}")

cat2, created6 = Categoria.objects.get_or_create(
    nome='Equipamentos Médicos',
    defaults={
        'descricao': 'Equipamentos e instrumentos médicos',
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created6 else '⚠️  Já existe'}: {cat2.nome}")

# 4. Criar Produtos
print("\n📦 Criando Produtos...")
prod1, created7 = Produto.objects.get_or_create(
    codigo='MED-001',
    instituicao=inst1,
    defaults={
        'nome': 'Dipirona 500mg',
        'descricao': 'Comprimido para dor e febre',
        'categoria': cat1,
        'quantidade_minima': 50,
        'quantidade_atual': 200,
        'preco_unitario': 1.50,
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created7 else '⚠️  Já existe'}: {prod1.nome}")

prod2, created8 = Produto.objects.get_or_create(
    codigo='EQUIP-001',
    instituicao=inst1,
    defaults={
        'nome': 'Termômetro Digital',
        'descricao': 'Termômetro infravermelhor digital',
        'categoria': cat2,
        'quantidade_minima': 10,
        'quantidade_atual': 45,
        'preco_unitario': 85.00,
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created8 else '⚠️  Já existe'}: {prod2.nome}")

prod3, created9 = Produto.objects.get_or_create(
    codigo='MED-002',
    instituicao=inst2,
    defaults={
        'nome': 'Amoxicilina 500mg',
        'descricao': 'Antibiótico em cápsula',
        'categoria': cat1,
        'quantidade_minima': 100,
        'quantidade_atual': 150,
        'preco_unitario': 2.80,
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created9 else '⚠️  Já existe'}: {prod3.nome}")

prod4, created10 = Produto.objects.get_or_create(
    codigo='EQUIP-002',
    instituicao=inst2,
    defaults={
        'nome': 'Estetoscópio',
        'descricao': 'Estetoscópio duplo de qualidade profissional',
        'categoria': cat2,
        'quantidade_minima': 5,
        'quantidade_atual': 8,
        'preco_unitario': 150.00,
        'ativo': True
    }
)
print(f"  {'✅ Criado' if created10 else '⚠️  Já existe'}: {prod4.nome}")

# 5. Criar Movimentações
print("\n📊 Criando Movimentações...")

# Entrada
mov1, created11 = Movimentacao.objects.get_or_create(
    id=1,
    defaults={
        'produto': prod1,
        'tipo': 'entrada',
        'quantidade': 100,
        'motivo': 'Compra de farmacêuticos',
        'funcionario': func1,
        'observacoes': 'Entrada de medicamentos do lote ABC123'
    }
) if not Movimentacao.objects.filter(id=1).exists() else (None, False)

if created11 or mov1:
    print(f"  ✅ Entrada: 100 unidades de {prod1.nome}")

# Saída
try:
    mov2 = Movimentacao(
        produto=prod2,
        tipo='saida',
        quantidade=5,
        motivo='Uso em consultas',
        funcionario=func1,
        observacoes='Saída para uso em consultório'
    )
    prod2.quantidade_atual -= 5
    prod2.save()
    mov2.save()
    print(f"  ✅ Saída: 5 unidades de {prod2.nome}")
except:
    print(f"  ⚠️  Saída já existe")

# Entrada em outra instituição
try:
    mov3 = Movimentacao(
        produto=prod3,
        tipo='entrada',
        quantidade=50,
        motivo='Reposição de estoque',
        funcionario=func2,
        observacoes='Compra para reposição do estoque'
    )
    prod3.quantidade_atual += 50
    prod3.save()
    mov3.save()
    print(f"  ✅ Entrada: 50 unidades de {prod3.nome}")
except:
    print(f"  ⚠️  Entrada já existe")

print("\n" + "=" * 80)
print("✅ DADOS DE EXEMPLO CRIADOS COM SUCESSO!")
print("=" * 80)
print("\n📊 Resumo:")
print(f"  • Instituições: {Instituicao.objects.count()}")
print(f"  • Funcionários: {Funcionario.objects.count()}")
print(f"  • Categorias: {Categoria.objects.count()}")
print(f"  • Produtos: {Produto.objects.count()}")
print(f"  • Movimentações: {Movimentacao.objects.count()}")
print("\n✨ Você pode acessar o sistema e conferir os dados!")
print("=" * 80 + "\n")
