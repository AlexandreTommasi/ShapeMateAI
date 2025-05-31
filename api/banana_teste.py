from fatsecret import Fatsecret

consumer_key = "7ca75b01710b411bb64af17a48a16b86"
consumer_secret = "10b74739b70a4fe48c29b17254f6eafe"

fs = Fatsecret(consumer_key, consumer_secret)

# Buscar por banana
resultados = fs.foods_search("Morango")

# Verificar o tipo e estrutura
# print("Tipo da resposta:", type(resultados))
# print("Resposta completa:\n", resultados)

print(dir(fs))
