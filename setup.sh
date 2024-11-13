#!/bin/bash

echo "=== Configurando ambiente do Dashboard de Chamados ==="

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python não encontrado! Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

# Verifica se virtualenv está instalado
if ! python3 -m pip show virtualenv &> /dev/null; then
    echo "Instalando virtualenv..."
    python3 -m pip install virtualenv
fi

# Cria e ativa ambiente virtual
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa o ambiente virtual
source venv/bin/activate

# Instala dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Executa migrações
echo "Executando migrações do banco de dados..."
python manage.py makemigrations
python manage.py migrate

# Cria superusuário se não existir
read -p "Deseja criar um superusuário? (s/N) " criar_super
if [[ $criar_super =~ ^[Ss]$ ]]; then
    python manage.py createsuperuser
fi

# Inicia o servidor
echo "=== Configuração concluída! ==="
echo "Para iniciar o servidor, execute: python manage.py runserver"
echo "Para ativar o ambiente virtual: source venv/bin/activate" 