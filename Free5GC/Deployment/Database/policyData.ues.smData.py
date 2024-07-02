import pymongo
from bson import ObjectId
from bson import Int64

# Conexão com o servidor do MongoDB. Alterar a porta específica do serviço do MongoDB
client = pymongo.MongoClient("mongodb://localhost:63145/")

# Acessa a base de dados e seleciona a coleção
db = client["free5gc"]
collection = db["policyData.ues.smData"]

# Define uma lista de documentos a ser passada para a base de dados posteriormente
documentos = []

# Define o valor inicial para o imsi
valor_inicial = "208930000000000"

# Define a quantidade de UEs que queira cadastrar
qtd_UE = 1000

# Cria os documentos 
for num_UE in range(qtd_UE):
    documento = {

        "smPolicySnssaiData": {
        "01010203": {
            "snssai": {
            "sst": 1,
            "sd": "010203"
            },
            "smPolicyDnnData": {
            "internet": {
                "dnn": "internet"
            },
            }
        }
        },
        "ueId": "imsi-"+str(int(valor_inicial) + num_UE),
}
    documentos.append(documento)

# Insere todos os documentos na coleção
resultado = collection.insert_many(documentos)
