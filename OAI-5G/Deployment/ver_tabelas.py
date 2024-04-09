import mysql.connector

# Conexão com o servidor MySQL. Altere as credenciais conforme necessário.
conn = mysql.connector.connect(
    host="localhost",
    port=33907,
    user="test",
    password="test",
    database="oai_db"
)

# Cria um cursor para executar as queries
cursor = conn.cursor()

# Define a query SQL para selecionar os dados inseridos
query = """
SELECT * FROM AuthenticationStatus
"""

# Executa a query
cursor.execute(query)

# Recupera todos os resultados
resultados = cursor.fetchall()

# Exibe os resultados
for row in resultados:
    print(row)

# Fecha a conexão
cursor.close()
conn.close()
