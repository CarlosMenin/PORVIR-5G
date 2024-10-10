import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from prometheus_pandas import query
from datetime import datetime
import re
import argparse

# URL do Prometheus
prometheus_url = "http://localhost:36463"

# Função para converter timestamps UNIX em formato de data legível
def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Função para arredondar a data e converter para UNIX timestamp
def redefine_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    if dt.second >= 30:
        dt = dt.replace(second=30, microsecond=0)
    else:
        dt = dt.replace(second=0, microsecond=0)
    return dt.timestamp()

# Função para normalizar os resultados da consulta
def normalize_result(result):
    result_str = result.to_string()
    result_list = re.split(r'[ \n]+', result_str)
    float_values = [float(value) for value in result_list if value.replace('.', '', 1).isdigit()]
    return float_values

# Função para calcular o valor máximo de uma lista de floats
def max_calc(float_values):
    if float_values:
        return max(float_values)
    return None

# Função para obter os dados de bytes recebidos de Prometheus e salvar em CSV
def get_receive_bytes(start_timestamp, end_timestamp, output_csv="output.csv"):
    global prometheus_url

    start = timestamp_to_datetime(start_timestamp)
    end = timestamp_to_datetime(end_timestamp)

    pastas = ['nrf', 'amf', 'ausf', 'nssf', 'pcf', 'smf', 'udm', 'udr']

    # Inicializa o DataFrame
    data = pd.DataFrame(index=pastas, columns=pastas)

    # Converter datas
    start = redefine_date(start)
    end = redefine_date(end)

    # Conectar ao Prometheus
    prometheus = query.Prometheus(prometheus_url)

    for i in range(len(pastas)):
        for j in range(len(pastas)):
            query_string = (
                f'sum(rate(istio_requests_total{{namespace="free5gc", source_app="free5gc-{pastas[i]}", '
                f'reporter="source", destination_app="free5gc-{pastas[j]}"}}[2m0s]))'
            )
            result = prometheus.query_range(query_string, start, end, "30s")
            normalized_values = normalize_result(result)
            max_value = max_calc(normalized_values)

            data.iloc[i, j] = max_value if max_value is not None else 0

    if data.isnull().all().all():
        print("Nenhum dado retornado do Prometheus.")
        return None

    data.to_csv(output_csv, index=True)
    return data

# Função para gerar e salvar o heatmap
def generate_heatmap(csv_file, output_image="heatmap.png"):
    data = pd.read_csv(csv_file, index_col=0)

    sns.set_theme()

    plt.figure(figsize=(10, 8))
    heatmap = sns.heatmap(data, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)

    plt.title('Requests per second', fontsize=16)
    plt.xlabel('Destination App', fontsize=14)
    plt.ylabel('Source App', fontsize=14)

    plt.tight_layout()

    # Salva o gráfico no formato PNG
    plt.savefig(output_image, dpi=300)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and visualize received bytes from Prometheus.")
    parser.add_argument("start_timestamp", type=int, help="Start UNIX timestamp")
    parser.add_argument("end_timestamp", type=int, help="End UNIX timestamp")
    parser.add_argument("--output_csv", type=str, default="output.csv", help="Output CSV file name")
    parser.add_argument("--output_image", type=str, default="heatmap.png", help="Output image file name")

    args = parser.parse_args()

    data = get_receive_bytes(args.start_timestamp, args.end_timestamp, args.output_csv)

    if data is not None:
        generate_heatmap(args.output_csv, args.output_image)

