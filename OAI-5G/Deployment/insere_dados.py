import mysql.connector

# Conexão com o servidor MySQL. Altere as credenciais conforme necessário.
conn = mysql.connector.connect(
    host="localhost",
    port=37499,
    user="test",
    password="test",
    database="oai_db"
)

# Cria um cursor para executar as queries
cursor = conn.cursor()

# Define a quantidade de UEs que você deseja cadastrar
qtd_UE = 1000

# Define a lista de usuários para inserção
usuarios = []

# Loop para gerar e adicionar usuários à lista
for num_UE in range(qtd_UE):
    ueid= 208950000000000 + (num_UE + 31)
    
    usuario = (
        ueid, 
        '5G_AKA', 
        '0C0A34601D4F07677303652C0462535B', 
        '0C0A34601D4F07677303652C0462535B', 
        '{"sqn": "000000000020", "sqnScheme": "NON_TIME_BASED", "lastIndexes": {"ausf": 0}}', 
        '8000', 
        'milenage', 
        '63bfa50ee6523365ff14c1f45f88737d', 
        None, 
        None, 
        None, 
        None, 
        ueid
    )
    
    usuarios.append(usuario)

# Define a query SQL para inserção
query = """
INSERT INTO AuthenticationSubscription (
    ueid,
    authenticationMethod,
    encPermanentKey,
    protectionParameterId,
    sequenceNumber,
    authenticationManagementField,
    algorithmId,
    encOpcKey,
    encTopcKey,
    vectorGenerationInHss,
    n5gcAuthMethod,
    rgAuthenticationInd,
    supi
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Executa a query para cada usuário
cursor.executemany(query, usuarios)

# Comita as alterações e fecha a conexão
conn.commit()
cursor.close()
conn.close()
