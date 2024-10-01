import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from prometheus_pandas import query
from datetime import datetime
import re
import argparse

prometeusUrl = "http://localhost:39461"

# Função para converter timestamps UNIX em formato de data
def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Função para converter datas e arredondar segundos
def redefineDate(d):
    dt = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
    if dt.second >= 30:
        dt = dt.replace(second=30, microsecond=0)
    else:
        dt = dt.replace(second=0, microsecond=0)
    # Converte para UNIX timestamp
    return dt.timestamp()

def normalizeResult(resultado):
    resultado = resultado.to_string()
    resultado = re.split(r'[ \n]+', resultado)
    valores_float = [float(valor) for valor in resultado if valor.replace('.', '', 1).isdigit()]
    return valores_float

def max_calc(valores_float):
    # Calcula o valor máximo
    if valores_float:  # Verifica se a lista não está vazia
        max_value = max(valores_float)  # Encontra o valor máximo
        return max_value
    else:
        return None  # Retorna None se não houver valores válidos

def getReceiveBytes(start_timestamp, end_timestamp, output_csv="output.csv"):
    global prometeusUrl

    # Converte os timestamps em datas
    start = timestamp_to_datetime(start_timestamp)
    end = timestamp_to_datetime(end_timestamp)

    print(start)

    pastas = ['nrf', 'amf', 'ausf', 'nssf', 'pcf', 'smf', 'udm', 'udr']

    # Inicializa o DataFrame para armazenar os resultados
    data = pd.DataFrame(index=pastas, columns=pastas)
    
    # Converter datas de entrada
    start = redefineDate(start)
    end = redefineDate(end)
    
    # Conectar ao Prometheus
    p = query.Prometheus(prometeusUrl)

    for i in range(len(pastas)):
        for j in range(len(pastas)):
            # Query Prometheus
            query_string = f'sum(rate(istio_requests_total{{namespace="free5gc", source_app="free5gc-{pastas[i]}", reporter="source", destination_app="free5gc-{pastas[j]}"}}[2m0s]))'
            result = p.query_range(
                query_string,
                start,
                end,
                "30s"
            )
            
            valores_normalizados = normalizeResult(result)  # Normaliza o resultado
            media_resultado = max_calc(valores_normalizados)  # Calcula o máximo

            if media_resultado is not None:  # Verifica se o máximo é válido
                data.iloc[i, j] = media_resultado
            else:
                data.iloc[i, j] = 0  # Define como 0 se não houver dados
        
    # Verificar se há dados retornados
    if data.isnull().all().all():  # Verifica se todas as entradas são NaN
        print("Nenhum dado retornado do Prometheus.")
        return None
    
    # Exportar dados para CSV
    data.to_csv(output_csv, index=True)  # Salva o DataFrame com o índice
    return data

def generate_heatmap(csv_file):
    # Carrega os dados do CSV
    data = pd.read_csv(csv_file, index_col=0)

    # Configura o estilo do Seaborn
    sns.set_theme()

    # Cria um heatmap
    plt.figure(figsize=(10, 8))  # Define o tamanho da figura

    # Usando a paleta 'coolwarm'
    heatmap = sns.heatmap(data, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)

    # Adiciona título
    plt.title('Heatmap de Recebimento de Bytes')

    # Exibe o gráfico
    plt.show()


if __name__ == "__main__":
    # Configuração do argparse
    parser = argparse.ArgumentParser(description="Obter e visualizar bytes recebidos de Prometheus.")
    parser.add_argument("start_timestamp", type=int, help="Timestamp UNIX de início")
    parser.add_argument("end_timestamp", type=int, help="Timestamp UNIX de fim")
    parser.add_argument("--output_csv", type=str, default="output.csv", help="Nome do arquivo CSV de saída")

    args = parser.parse_args()

    # Chamada da função com os timestamps fornecidos
    data = getReceiveBytes(args.start_timestamp, args.end_timestamp, args.output_csv)

    # Gera o heatmap a partir do CSV, se os dados foram retornados
    if data is not None:
        generate_heatmap(args.output_csv)
