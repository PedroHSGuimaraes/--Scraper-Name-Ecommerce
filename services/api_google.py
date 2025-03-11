
from googleapiclient.discovery import build

def pesquisa_google(chave_api, id_mecanismo, consulta):
  """
  Executa uma pesquisa no Google usando a API Custom Search JSON.

  Args:
    chave_api: Sua chave de API do Google Cloud Console.
    id_mecanismo: O ID do seu mecanismo de pesquisa personalizada.
    consulta: A consulta de pesquisa.

  Returns:
    Uma lista de resultados da pesquisa ou None em caso de erro.
  """
  try:
    servico = build("customsearch", "v1", developerKey=chave_api)
    requisicao = servico.cse().list(q=consulta, cx=id_mecanismo)
    resposta = requisicao.execute()
    return resposta.get("items")
  except Exception as erro:
    print(f"Ocorreu um erro: {erro}")
    return None

# Substitua pelas suas credenciais e consulta
chave_api = "AIzaSyDkwgWLJ_NISwA6Nk-4X0__e68jRK7eyLw"
id_mecanismo = "47366a2537ee841e9"
consulta = "Python"

resultados = pesquisa_google(chave_api, id_mecanismo, consulta)

if resultados:
  for resultado in resultados:
    print(resultado["title"])
    print(resultado["link"])
    print(resultado["snippet"])
    print("-" * 20)
else:
  print("Nenhum resultado encontrado.")