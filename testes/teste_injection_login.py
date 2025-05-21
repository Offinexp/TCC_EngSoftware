import pytest
from app import app, db, Usuario

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Cria um usuário real para comparação
            user = Usuario(nome='Teste', email='teste@teste.com')
            user.set_senha('senhaSegura')
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_login_sql_injection(client):
    injection_payload = "' OR '1'='1"
    response = client.post('/login', data={
        'email': injection_payload,
        'senha': injection_payload
    }, follow_redirects=True)

    assert 'Credenciais inválidas'.encode('utf-8') in response.data
