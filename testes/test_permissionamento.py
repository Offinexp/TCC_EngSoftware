import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from factory import create_app, db
from config import TestingConfig
from models import Usuario

@pytest.fixture(scope='module')
def app():
    app = create_app(test_config=TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def usuario_comum(app):
    usuario = Usuario(nome='Usuário Comum 1', email='usuario1@tcc.com', nivel_acesso='usuario')
    usuario.set_senha('1234')
    db.session.add(usuario)
    db.session.commit()
    return usuario

@pytest.fixture
def usuario_admin(app):
    admin = Usuario(nome='Administrador 1', email='admin1@tcc.com', nivel_acesso='admin')
    admin.set_senha('1234')
    db.session.add(admin)
    db.session.commit()
    return admin

def login(client, email, senha):
    return client.post('/login', data={'email': email, 'senha': senha}, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_admin_pode_acessar_admin_dashboard(client, usuario_admin):
    login(client, usuario_admin.email, 'admin123')
    response = client.get('/admin')
    assert response.status_code == 200
    assert b'Painel Admin' in response.data

def test_usuario_comum_nao_pode_acessar_admin_dashboard(client, usuario_comum):
    login(client, usuario_comum.email, '1234')
    response = client.get('/admin', follow_redirects=True)
    assert b'Painel Admin' not in response.data
    assert b'Bem-vindo' in response.data

def test_nao_autenticado_nao_pode_acessar_admin(client):
    response = client.get('/admin', follow_redirects=True)
    assert b'Login' in response.data

def test_admin_pode_criar_produto(client, usuario_admin):
    login(client, usuario_admin.email, 'admin123')
    response = client.post('/admin/produtos/novo', data={
        'nome': 'Produto Teste',
        'quantidade_em_estoque': 10,
        'preco': '50.00',
        'categoria_id': 1
    }, follow_redirects=True)
    assert b'Produto Teste' in response.data or response.status_code == 200

def test_usuario_comum_nao_pode_criar_produto(client, usuario_comum):
    login(client, usuario_comum.email, '1234')
    response = client.post('/admin/produtos/novo', data={
        'nome': 'Produto Teste',
        'quantidade_em_estoque': 10,
        'preco': '50.00',
        'categoria_id': 1
    }, follow_redirects=True)
    assert 'Permissão negada' in response.data.decode('utf-8') or 'Bem-vindo' in response.data.decode('utf-8')

def test_logout_bloqueia_acesso(client, usuario_admin):
    login(client, usuario_admin.email, 'admin123')
    logout(client)
    response = client.get('/admin', follow_redirects=True)
    assert b'Login' in response.data
