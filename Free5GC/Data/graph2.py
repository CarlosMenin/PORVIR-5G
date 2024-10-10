import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Definindo o diretório de trabalho
pasta = os.getcwd()  

# Nomes das colunas e cores
column_names = ['MM5G_REGISTERED_INITIATED', 'MM5G_REGISTERED', 'DataPlaneReady']
colors = ['green', 'orange', 'red']

# Dicionário para armazenar dados agrupados por título
dados_agrupados = {}

# Processar todos os arquivos CSV
for arquivo in os.listdir(pasta):
    if arquivo.endswith(".csv"):
        nome_arquivo = os.path.splitext(arquivo)[0]

        # Criar título baseado no nome do arquivo
        if "div" in nome_arquivo:
            title = f'Starting at {nome_arquivo.split("_")[4]}ms,\n Dividing by {nome_arquivo.split("_")[5]}\n Every {nome_arquivo.split("_")[6]} Connections'
        elif "dec" in nome_arquivo:
            title = f'Starting at {nome_arquivo.split("_")[4]}ms,\n Decreased by {nome_arquivo.split("_")[5]}\n Every {nome_arquivo.split("_")[6]} Connections'
        else:
            title = f'Interval of {nome_arquivo.split("_")[3]}ms'

        base_filename = os.path.join(pasta, arquivo)

        # Ler e ordenar os dados
        try:
            dados = pd.read_csv(base_filename)
            dados = dados.sort_values(by=dados.columns[0])

            # Se o título já existir no dicionário, acumular os dados
            if title in dados_agrupados:
                for column in column_names:
                    dados_agrupados[title][column].extend(dados[column].dropna().to_numpy())
            else:
                dados_agrupados[title] = {column: dados[column].dropna().to_numpy().tolist() for column in column_names}

        except Exception as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")

# Criar gráfico de barras para cada título agrupado
plt.figure(figsize=(12, 8))

# Posições no eixo x para as barras
bar_positions = np.arange(len(dados_agrupados))  # Posições base das barras

# Inicializar um array para armazenar as médias acumuladas
acumuladas = np.zeros(len(dados_agrupados))

# Plotar as médias para cada título empilhado
for column_index, column in enumerate(column_names):
    medias = [np.mean(dados_agrupados[title][column]) for title in dados_agrupados]  # Média para cada título
    plt.bar(bar_positions, medias, bottom=acumuladas, color=colors[column_index], alpha=0.7, label=column)
    acumuladas += medias  # Atualiza as médias acumuladas para a próxima coluna

# Configurações do gráfico
plt.title('Média de Tempo para Conexão por Título', fontsize=14)
plt.xlabel('Títulos', fontsize=12)
plt.ylabel('Tempo Médio de Conexão (ms)', fontsize=12)
plt.xticks(bar_positions, list(dados_agrupados.keys()), rotation=30)  # Ajuste para o eixo x
plt.legend(loc='upper right', fontsize='small')
plt.tight_layout()

# Salvar o gráfico
novo_nome_arquivo = 'bar_graphs_combined_stacked.png'
try:
    plt.savefig(novo_nome_arquivo, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo: {novo_nome_arquivo}")  # Log de salvamento
except Exception as e:
    print(f"Erro ao salvar o gráfico {novo_nome_arquivo}: {e}")

plt.show()  # Adicionando para mostrar o gráfico
