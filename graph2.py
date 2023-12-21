import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pasta = os.getcwd()  

column_names = ['MM5G_REGISTERED_INITIATED',
                'MM5G_REGISTERED', 'DataPlaneReady']
colors = ['green', 'orange', 'red']

for arquivo in os.listdir(pasta):
    if arquivo.endswith(".csv"):
        nome_arquivo = os.path.splitext(arquivo)[0]
        teste = nome_arquivo.split("_")[2]

        base_filename = os.path.join(pasta, arquivo)

        dados = pd.read_csv(base_filename)
        dados = dados.sort_values(by=dados.columns[0])

        stacked_data = np.zeros(len(dados))

        plt.figure(figsize=(10, 6)) 

        for column_index, column_name in enumerate(column_names):
            column_data = np.array(dados[column_name])
            diff_column_data = column_data - stacked_data

            plt.fill_between(dados['gnbid'], stacked_data, stacked_data + diff_column_data,
                             label='{}'.format(column_name), color=colors[column_index], alpha=1, linewidth=2)

            stacked_data += diff_column_data

        # Criar o título baseado no nome do arquivo
        if "div" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[3]}ms, Dividing by {nome_arquivo.split("_")[4]} Every {nome_arquivo.split("_")[5]} Connections'
            novo_nome_arquivo = f'graph_times_div_{nome_arquivo.split("_")[3]}_{nome_arquivo.split("_")[4]}_{nome_arquivo.split("_")[5]}.png'
        elif "dec" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[3]}ms, Decreased by {nome_arquivo.split("_")[4]} Every {nome_arquivo.split("_")[5]} Connections'
            novo_nome_arquivo = f'graph_times_dec_{nome_arquivo.split("_")[3]}_{nome_arquivo.split("_")[4]}_{nome_arquivo.split("_")[5]}.png'
        else:
            title = f'Parallel Connection Test:\nInterval of {nome_arquivo.split("_")[3]}ms'
            novo_nome_arquivo = f'graph_times_{nome_arquivo.split("_")[2]}_{nome_arquivo.split("_")[3]}.png'

        # Adicionar título e labels
        plt.title(title, fontsize=14)
        plt.xlabel('UE Number', fontsize=12)
        plt.ylabel('Time to Connection (ms)', fontsize=12)
        plt.legend(loc='upper right', fontsize='small')
        plt.tight_layout()

        # Salvar o gráfico com o nome adequado
        plt.savefig(novo_nome_arquivo, dpi=300, bbox_inches='tight')
        plt.close()

# Remova plt.show() se não quiser exibir os gráficos na tela
