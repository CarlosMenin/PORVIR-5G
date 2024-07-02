import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pasta = os.getcwd()
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
          'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

for arquivo in os.listdir(pasta):
    if arquivo.endswith(".csv"):
        nome_arquivo = os.path.splitext(arquivo)[0]
        base_filename = os.path.join(pasta, arquivo)

        dados = pd.read_csv(base_filename)
        timestamp_base = dados.iloc[0]['timestamp']
        dados = dados.sort_values(by=dados.columns[0])

        plt.figure(figsize=(10, 6))

        for i in range(0, len(dados), 100):
            timestamp = np.array([])
            connections = np.array([])
            grupo = dados.iloc[i:i+100].copy()

            for indice, linha in grupo.iterrows():
                timestamp = np.append(timestamp, (linha['timestamp']-timestamp_base)/1000000000)
                connections = np.append(connections, linha['DataPlaneReady'])

            cor = colors[i // 100 % len(colors)] 

            plt.scatter(timestamp, connections, label="Tester {}".format(grupo.iloc[0, 0]), color=cor, s=5, alpha=1)

        # Criar o título baseado no nome do arquivo
        if "div" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[4]}ms, Dividing by {nome_arquivo.split("_")[5]} Every {nome_arquivo.split("_")[6]} Connections'
            novo_nome_arquivo = f'graph_connections_div_{nome_arquivo.split("_")[4]}_{nome_arquivo.split("_")[5]}_{nome_arquivo.split("_")[6]}.png'
        elif "dec" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[4]}ms, Decreased by {nome_arquivo.split("_")[5]} Every {nome_arquivo.split("_")[6]} Connections'
            novo_nome_arquivo = f'graph_connections_dec_{nome_arquivo.split("_")[4]}_{nome_arquivo.split("_")[5]}_{nome_arquivo.split("_")[6]}.png'
        else:
            title = f'Parallel Connection Test:\nInterval of {nome_arquivo.split("_")[3]}ms'
            novo_nome_arquivo = f'graph_connections_{nome_arquivo.split("_")[1]}_{nome_arquivo.split("_")[3]}.png'

        # Adicionar título e labels
        plt.title(title, fontsize=14)
        plt.xlabel('Experiment Time (s)', fontsize=12)
        plt.ylabel('Time to Connection (ms)', fontsize=12)
        plt.legend(loc='upper right', fontsize='small')
        plt.grid(True)
        plt.tight_layout()

        # Salvar o gráfico com o nome adequado
        plt.savefig(novo_nome_arquivo, dpi=300, bbox_inches='tight')
        plt.close()

# Remova plt.show() se não quiser exibir os gráficos na tela
