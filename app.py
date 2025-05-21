from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from mysql import connector

# Configuração do Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicialização do banco de dados e login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelos do banco de dados

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'  # nome da tabela no banco

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    nivel_acesso = db.Column(db.String(10), default='usuario')
    
    def set_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)


class Produto(db.Model):
    __tablename__ = 'produtos'  # nome correto da tabela

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    quantidade_em_estoque = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    categoria = db.relationship('Categoria', backref='produtos')


# Função para carregar o usuário
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))  # Classe com U maiúsculo

# Rotas

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()  # Classe Usuario com U maiúsculo
        if usuario and usuario.verificar_senha(senha):          # Variável usuario minúsculo
            login_user(usuario)
            return redirect(url_for('dashboard'))
        flash('Credenciais inválidas!', 'danger')
    return render_template('login.html')

@app.route('/admin/produtos/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    if current_user.nivel_acesso != 'admin':
        return redirect(url_for('dashboard'))
    
    categorias = Categoria.query.all()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = int(request.form['quantidade'])
        preco = float(request.form['preco'])
        categoria_id = int(request.form['categoria'])

        novo = Produto(
            nome=nome,
            descricao=descricao,
            quantidade_em_estoque=quantidade,
            preco=preco,
            categoria_id=categoria_id
        )
        db.session.add(novo)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('novo_produto.html', categorias=categorias)


@app.route('/admin/produtos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    if current_user.nivel_acesso != 'admin':
        return redirect(url_for('dashboard'))
    
    produto = Produto.query.get_or_404(id)
    categorias = Categoria.query.all()

    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.quantidade_em_estoque = int(request.form['quantidade'])
        produto.preco = float(request.form['preco'])
        produto.categoria_id = int(request.form['categoria'])

        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('editar_produto.html', produto=produto, categorias=categorias)


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.nivel_acesso == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.nivel_acesso != 'admin':
        return redirect(url_for('dashboard'))
    produtos = Produto.query.all()
    return render_template('admin_dashboard.html', produtos=produtos)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rodar a aplicação
if __name__ == '__main__':
    app.run(debug=True)
