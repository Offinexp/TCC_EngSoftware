import time
import subprocess
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, Usuario

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

pasta_relatorios = os.path.join(diretorio_atual, "relatorios")
os.makedirs(pasta_relatorios, exist_ok=True)

arquivo_relatorio = os.path.join(pasta_relatorios, "relatorio.html")

while True:
    print("Executando os testes...")

    subprocess.run([
        "pytest",
        "--html=" + arquivo_relatorio,
        "--self-contained-html"
    ])

    print("Testes finalizados. Aguardando 5 minutos para próxima execução...")
    time.sleep(300)
