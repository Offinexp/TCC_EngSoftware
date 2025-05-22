import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from factory import db, create_app
from config import TestingConfig
from models import Usuario, Produto, Categoria

@pytest.fixture(scope='module')
def app():
    app = create_app(test_config=TestingConfig)
    with app.app_context():
        db.create_all()
        print("\n✅ Banco de dados criado para os testes de produtos.")
        yield app
        db.session.remove()
        db.drop_all()
        print("🧹 Banco de dados limpo após os testes de produtos.")

@pytest.fixture(scope='module')
def test_client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def init_user(app):
    with app.app_context():
        user = Usuario(nome='Administrador2', email='admin2@tcc.com', nivel_acesso='admin')
        user.set_senha('1234')
        db.session.add(user)
        db.session.commit()
        print("\n👤 Usuário administrador criado para testes.")
        yield user
        db.session.delete(user)
        db.session.commit()
        print("🧹 Usuário administrador removido após testes.")

@pytest.fixture(scope='module')
def categoria_existente(app):
    with app.app_context():
        categoria = Categoria(nome='Categoria Teste')
        db.session.add(categoria)
        db.session.commit()
        print("\n📂 Categoria criada para teste.")
        yield categoria
        db.session.delete(categoria)
        db.session.commit()
        print("🧹 Categoria removida após teste.")

@pytest.fixture(scope='module')
def authenticated_client(test_client, init_user):
    print("\n🔐 Efetuando login do usuário administrador para testes...")
    login_response = test_client.post('/login', data={
        'email': init_user.email,
        'senha': '1234'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    print("✅ Login realizado com sucesso.")
    return test_client

def test_injecao_sql_com_aspas(authenticated_client, app, categoria_existente):
    injection_payload = "'; DROP TABLE produtos; --"
    print("\n🧪 Teste: Injeção SQL com aspas")
    print(f"Payload: {injection_payload}")

    response = authenticated_client.post('/admin/produtos/novo', data={
        'nome': injection_payload,
        'descricao': 'Descrição segura',
        'quantidade': '10',
        'preco': '100.00',
        'categoria': str(categoria_existente.id)
    }, follow_redirects=True)
    assert response.status_code == 200

    html_text = response.data.decode('utf-8')
    import html as html_lib
    unescaped_text = html_lib.unescape(html_text)

    assert injection_payload in unescaped_text
    print("✅ Payload exibido como texto no HTML, sem execução da injeção.")

def test_injecao_sql_sem_aspas(authenticated_client, app, categoria_existente):
    injection_payload = "1; DROP TABLE produtos;"
    print("\n🧪 Teste: Injeção SQL sem aspas")
    print(f"Payload: {injection_payload}")

    response = authenticated_client.post('/admin/produtos/novo', data={
        'nome': injection_payload,
        'descricao': 'Descricao segura',
        'quantidade': '10',
        'preco': '100.00',
        'categoria': str(categoria_existente.id)
    }, follow_redirects=True)
    assert response.status_code == 200
    assert injection_payload.encode() in response.data

    with app.app_context():
        produto = Produto.query.filter_by(nome=injection_payload).first()
        assert produto is not None

    print("✅ Produto criado com payload armazenado como texto. Sem execução maliciosa.")

def test_injecao_sql_com_comment(authenticated_client, app, categoria_existente):
    injection_payload = "' OR 1=1 --"
    print("\n🧪 Teste: Injeção SQL com comentário --")
    print(f"Payload: {injection_payload}")

    response = authenticated_client.post('/admin/produtos/novo', data={
        'nome': injection_payload,
        'descricao': 'Descricao segura',
        'quantidade': '10',
        'preco': '100.00',
        'categoria': str(categoria_existente.id)
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"&#39; OR 1=1 --" in response.data
    print("✅ Payload exibido corretamente no HTML, sem falhas no banco.")

def test_tabela_produtos_nao_excluida(authenticated_client, app):
    print("\n🔍 Verificação: tabela produtos intacta")
    with app.app_context():
        try:
            produtos = Produto.query.all()
            print(f"✅ Tabela produtos está intacta. Total de produtos: {len(produtos)}")
            assert produtos is not None
        except Exception as e:
            pytest.fail(f"❌ Tabela produtos foi alterada ou excluída: {e}")
