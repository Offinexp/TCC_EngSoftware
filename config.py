import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)  # Chave secreta para o Flask
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:12583214@localhost/estoque_db'
