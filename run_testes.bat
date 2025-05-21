@echo off
REM Define a data/hora para o nome do arquivo
set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
REM Remove espaços do timestamp
set timestamp=%timestamp: =0%

REM Ativa ambiente virtual (se usar)
REM call C:\caminho\para\seu\venv\Scripts\activate.bat

REM Roda o pytest e salva relatório com timestamp
pytest --html=relatorios\relatorio_%timestamp%.html --self-contained-html

REM Pausa para ver mensagem 
pause
