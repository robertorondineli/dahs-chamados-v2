@echo off
echo === Configurando ambiente do Dashboard de Chamados ===

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado! Por favor, instale o Python 3.8 ou superior.
    exit /b 1
)

:: Verifica se virtualenv está instalado
python -m pip show virtualenv >nul 2>&1
if errorlevel 1 (
    echo Instalando virtualenv...
    python -m pip install virtualenv
)

:: Cria e ativa ambiente virtual
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

:: Ativa o ambiente virtual
call venv\Scripts\activate

:: Instala dependências
echo Instalando dependencias...
python -m pip install -r requirements.txt

:: Executa migrações
echo Executando migracoes do banco de dados...
python manage.py makemigrations
python manage.py migrate

:: Cria superusuário se não existir
echo Deseja criar um superusuario? (S/N)
set /p criar_super=
if /i "%criar_super%"=="S" (
    python manage.py createsuperuser
)

:: Inicia o servidor
echo === Configuracao concluida! ===
echo Para iniciar o servidor, execute: python manage.py runserver
echo Para ativar o ambiente virtual: venv\Scripts\activate

pause 