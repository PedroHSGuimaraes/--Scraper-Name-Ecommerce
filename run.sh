#!/bin/bash

# Verificar se o ambiente virtual Python existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Garantir que a estrutura de diretórios existe
mkdir -p resultados

# Executar aplicação
echo "Iniciando aplicação..."
python main.py "$@"
