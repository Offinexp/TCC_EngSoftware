import pytest
from app import app, db, Usuario, Produto  # importa seu app, banco e modelos

def test_injecao_sql_no_cadastro_produto(client, app):
    # Primeiro loga como admin para conseguir acessar a rota protegida
    with app.app_context():
        admin = Usuario(nome='Admin', email='admin@teste.com', nivel_acesso='admin')
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()

    # Login
    client.post('/login', data={'email': 'admin@teste.com', 'senha': 'admin123'})

    # Payload de injeção no nome do produto
    injection_payload = "'; DROP TABLE produtos; --"

    response = client.post('/admin/produtos/novo', data={
        'nome': injection_payload,
        'descricao': 'Descricao normal',
        'quantidade': '10',
        'preco': '100.00',
        'categoria': '1'  # Assumindo que categoria com id 1 exista
    }, follow_redirects=True)

    # Verifica que a resposta continua OK e não quebrou
    assert response.status_code == 200
    # Verifica que a mensagem de sucesso aparece (produto foi cadastrado)
    assert b'Produto cadastrado com sucesso!' in response.data

    # Verifica se o produto foi realmente cadastrado com o nome injetado como texto (não executado)
    produto = Produto.query.filter_by(nome=injection_payload).first()
    assert produto is not None
