import json

# Criar um arquivo de exemplo com algumas lojas
lojas_teste = [
    {"nome": "Samsung Brasil", "url": "https://www.samsung.com/br/"},
    {"nome": "Apple Brasil", "url": "https://www.apple.com/br/"},
    {"nome": "Nike Brasil", "url": "https://www.nike.com.br/"}
]

# Salvar no formato esperado pelo script
with open("lojas_oficiais_parcial.json", "w", encoding="utf-8") as f:
    json.dump(lojas_teste, f, ensure_ascii=False, indent=2)

print("Arquivo de teste criado com sucesso!")
