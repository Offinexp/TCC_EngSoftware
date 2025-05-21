import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, Usuario

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def usuario_comum(client):
    usuario = Usuario(nome='Usuário Comum', email='usuario1@tcc.com', nivel_acesso='usuario')
    usuario.set_senha('1234')
    db.session.add(usuario)
    db.session.commit()
    return usuario

def test_usuario_nao_admin_nao_pode_acessar_admin_dashboard(client, usuario_comum):
    client.post('/login', data={'email': usuario_comum.email, 'senha': '1234'})
    response = client.get('/admin', follow_redirects=True)
    assert b'Painel Admin' not in response.data
    assert b'Bem-vindo' in response.data

def test_usuario_comum_tentando_criar_produto(client, usuario_comum):
    print("Entrou no segundo teste")
    client.post('/login', data={'email': usuario_comum.email, 'senha': '1234'})
    response = client.get('/admin/produtos/novo', follow_redirects=True)
    print(response.data.decode())
    assert b'Cadastrar Produto' not in response.data
    assert b'Bem-vindo' in response.data
