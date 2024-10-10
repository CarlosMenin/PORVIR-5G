import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from prometheus_pandas import query
from datetime import datetime
import re
import argparse

# URL do Prometheus
prometheus_url = "http://localhost:36463"

# Função para converter timestamps UNIX em formato legível
def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Função para arredondar a data e converter para UNIX timestamp
def redefine_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(second=30 if dt.second >= 30 else 0, microsecond=0)
    return dt.timestamp()

# Normaliza o resultado da consulta
def normalize_result(result):
    return [float(value) for value in re.findall(r'\d+\.\d+', result.to_string())]

def mean_calc(float_values):
    if float_values:
        return sum(float_values)/len(float_values)
    return None

# Função para obter os dados de bytes recebidos de Prometheus e salvar em CSV
def get_receive_bytes(start_end_timestamps, output_csv="output.csv"):
    pastas = ['nrf', 'amf', 'ausf', 'nssf', 'pcf', 'smf', 'udm', 'udr']
    prometheus = query.Prometheus(prometheus_url)
    
    combined_data = pd.DataFrame(index=pastas, columns=pastas)

    for start, end in start_end_timestamps:
        start = redefine_date(timestamp_to_datetime(start))
        end = redefine_date(timestamp_to_datetime(end))
        
        data = pd.DataFrame(index=pastas, columns=pastas)
        
        for i, source_app in enumerate(pastas):
            for j, dest_app in enumerate(pastas):
                query_string = (
                                    f'sum by(destination_app) (istio_requests_total{{namespace="free5gc", '
                                    f'source_app="free5gc-{pastas[i]}", reporter="source", '
                                    f'response_code="503", destination_app="free5gc-{pastas[j]}"}})'
                                )
                result = prometheus.query_range(query_string, start, end, "30s")
                normalized_values = normalize_result(result)
                data.iloc[i, j] = mean_calc(normalized_values) if normalized_values else 0

        # Acumular os dados de cada intervalo de tempo nos componentes correspondentes
        combined_data = combined_data.add(data, fill_value=0)

    # Remove as linhas e colunas que contenham apenas zeros
    combined_data = combined_data.loc[(combined_data != 0).any(axis=1), (combined_data != 0).any(axis=0)]

    combined_data.to_csv(output_csv)
    return combined_data

# Gera o gráfico de calor agregando dados por componente
def generate_scientific_heatmap(csv_file, output_image="heatmap.png"):
    data = pd.read_csv(csv_file, index_col=0)
    
    # Remove as linhas e colunas que contenham apenas zeros
    data = data.loc[(data != 0).any(axis=1), (data != 0).any(axis=0)]
    
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "axes.grid": True, 
        "grid.linestyle": "--",
        "grid.color": "gray",
        "grid.alpha": 0.7
    })

    plt.figure(figsize=(10, 8))
    sns.heatmap(data, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
    
    plt.title('Requests per Second (Aggregated per Component)', fontsize=16)
    plt.xlabel('Destination App', fontsize=12)
    plt.ylabel('Source App', fontsize=12)
    plt.tight_layout()
    
    plt.savefig(output_image, dpi=300)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and visualize metrics from Prometheus.")
    parser.add_argument("start_end_timestamps", type=str, help="List of start and end UNIX timestamps as tuples. Example: '[(start1, end1), (start2, end2)]'")
    parser.add_argument("--output_csv", type=str, default="output.csv", help="Output CSV file name")
    parser.add_argument("--output_image", type=str, default="heatmap.png", help="Output image file name")

    args = parser.parse_args()

    # Converta a string do argumento em uma lista de tuplas
    start_end_timestamps = eval(args.start_end_timestamps)

    data = get_receive_bytes(start_end_timestamps, args.output_csv)
    if data is not None:
        generate_scientific_heatmap(args.output_csv, args.output_image)
