import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from factory import db, create_app
from config import TestingConfig
from models import Usuario

@pytest.fixture
def test_client():
    app = create_app(test_config=TestingConfig)

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def init_user():
    app = create_app(test_config=TestingConfig)
    with app.app_context():
        user = Usuario(nome='Administrador4', email='admin4@tcc.com')
        user.set_senha('1234')
        db.session.add(user)
        db.session.commit()
        print("\n✅ Usuário de teste criado: admin4@tcc.com / 1234")
        yield user
        db.session.delete(user)
        db.session.commit()
        print("🧹 Usuário de teste removido.")

def test_login_sql_injection(test_client, init_user):
    payload = "' OR '1'='1"
    print(f"\n🔐 Teste: SQL Injection com OR '1'='1'")
    print(f"Payload utilizado: {payload}")
    response = test_client.post('/login', data={
        'email': payload,
        'senha': payload
    }, follow_redirects=True)

    print("➡️ Verificando se login foi bloqueado...")
    assert 'Credenciais inválidas'.encode('utf-8') in response.data
    print("✅ Login bloqueado com sucesso.")

def test_login_sql_injection_drop_table(test_client, init_user):
    payload = "'; DROP TABLE usuario; --"
    print(f"\n💣 Teste: SQL Injection para DROP TABLE")
    print(f"Payload utilizado: {payload}")
    response = test_client.post('/login', data={
        'email': payload,
        'senha': 'qualquer'
    }, follow_redirects=True)

    print("➡️ Verificando resposta da aplicação...")
    assert 'Credenciais inválidas'.encode('utf-8') in response.data
    print("✅ Resposta correta para tentativa de DROP.")

    try:
        usuarios = Usuario.query.all()
        print(f"✅ Tabela 'usuario' continua existente. Total de usuários: {len(usuarios)}")
    except Exception as e:
        pytest.fail(f"❌ ERRO: Tabela 'usuario' pode ter sido removida! {e}")

def test_login_sql_injection_comment(test_client, init_user):
    payload = "' OR 1=1 --"
    print(f"\n🧪 Teste: SQL Injection com comentário '--'")
    print(f"Payload utilizado: {payload}")
    response = test_client.post('/login', data={
        'email': payload,
        'senha': 'qualquer'
    }, follow_redirects=True)

    print("➡️ Verificando se login foi bloqueado...")
    assert 'Credenciais inválidas'.encode('utf-8') in response.data
    print("✅ Login bloqueado com sucesso.")
