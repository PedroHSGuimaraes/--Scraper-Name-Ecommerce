#!/bin/bash

<<<<<<< HEAD
# Script de inicialização do projeto
# Este script configura o ambiente e executa a aplicação
# 
# O que este script faz:
# 1. Verifica e cria um ambiente virtual Python
# 2. Instala todas as dependências necessárias
# 3. Cria a estrutura de diretórios
# 4. Executa a aplicação

# Verificar se o ambiente virtual Python existe
# O ambiente virtual (venv) é uma instalação Python isolada
# que não interfere com outras instalações no sistema
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv    # Cria um novo ambiente virtual chamado 'venv'
fi

# Ativar ambiente virtual
# Isso garante que usaremos o Python e as bibliotecas
# instaladas no ambiente virtual, não as do sistema
source venv/bin/activate

# Instalar dependências
# O arquivo requirements.txt contém a lista de todas as
# bibliotecas Python necessárias para rodar a aplicação
=======
# Verificar se o ambiente virtual Python existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
>>>>>>> origin/main
echo "Instalando dependências..."
pip install -r requirements.txt

# Garantir que a estrutura de diretórios existe
<<<<<<< HEAD
# Cria o diretório 'resultados' se ele não existir
# Este diretório será usado para salvar os dados extraídos
mkdir -p resultados

# Executar aplicação
# Inicia o script principal (main.py) passando todos os
# argumentos recebidos na linha de comando ($@)
=======
mkdir -p resultados

# Executar aplicação
>>>>>>> origin/main
echo "Iniciando aplicação..."
python main.py "$@"
