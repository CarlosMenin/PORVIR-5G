import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from prometheus_pandas import query
from datetime import datetime
import re
import argparse

prometheus_url = "http://localhost:36463"
pastas = ['upf', 'mongo', 'nrf', 'amf', 'ausf', 'nssf', 'pcf', 'smf', 'udm', 'udr', 'webui']

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def redefine_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(second=30 if dt.second >= 30 else 0, microsecond=0)
    return dt.timestamp()

def normalize_result(result):
    return [float(value) for value in re.findall(r'\d+\.\d+', result.to_string())]

def mean_calc(float_values):
    return sum(float_values) / len(float_values) if float_values else 0

def fetch_metrics(query_string, start, end):
    prometheus = query.Prometheus(prometheus_url)
    result = prometheus.query_range(query_string, start, end, "30s")
    return normalize_result(result)

def get_combined_metrics_data(start_end_timestamps, output_csv="output.csv"):
    data = pd.DataFrame(index=pastas, columns=["mean_cpu_usage", "mean_memory_usage", "mean_receive_bytes", "mean_transmit_bytes"])

    metrics = {
        "mean_cpu_usage": 'sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{cluster="", namespace="free5gc"} * on(namespace,pod) group_left(workload, workload_type)',
        "mean_memory_usage": 'sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", namespace="free5gc", container!="", image!=""} * on(namespace,pod) group_left(workload, workload_type)',
        "mean_receive_bytes": 'sum(rate(container_network_receive_bytes_total{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", namespace="free5gc"}[2m0s]) * on (namespace,pod) group_left(workload,workload_type)',
        "mean_transmit_bytes": 'sum(rate(container_network_transmit_bytes_total{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", namespace="free5gc"}[2m0s]) * on (namespace,pod) group_left(workload,workload_type)'
    }

    combined_data = []

    for start, end in start_end_timestamps:
        start, end = redefine_date(timestamp_to_datetime(start)), redefine_date(timestamp_to_datetime(end))
        interval_data = data.copy()

        for pasta in pastas:
            for metric_col, query_string in metrics.items():
                query_string += f' namespace_workload_pod:kube_pod_owner:relabel{{cluster="", namespace="free5gc", workload="free5gc-{pasta}"}}) by (workload)'
                mean_value = mean_calc(fetch_metrics(query_string, start, end))
                interval_data.at[pasta, metric_col] = mean_value

        interval_data['interval'] = f"{start}-{end}"
        combined_data.append(interval_data)

    full_data = pd.concat(combined_data)
    full_data.to_csv(output_csv)
    return full_data

def generate_combined_boxplots_per_component(csv_file, output_image="combined_boxplots.png"):
    data = pd.read_csv(csv_file, index_col=0)
    sns.set_theme()

    # Configurações específicas para gráficos científicos
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.linestyle": "--",
        "grid.color": "gray",
        "grid.alpha": 0.7
    })

    metrics = ["mean_cpu_usage", "mean_memory_usage", "mean_receive_bytes", "mean_transmit_bytes"]
    titles = ['CPU Usage', 'Memory Usage', 'Receive Bytes', 'Transmit Bytes']

    # Criando uma figura com 4 subplots (um para cada métrica)
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    axs = axs.flatten()

    for i, metric in enumerate(metrics):
        # Criando um boxplot para cada métrica, com box-plots separados para cada componente (pasta)
        sns.boxplot(x='index', y=metric, data=data.reset_index(), ax=axs[i], palette="Blues", legend=False)
        axs[i].set_title(titles[i], fontsize=14)
        axs[i].set_xlabel('Component (Pasta)')
        axs[i].set_ylabel(f'{titles[i]} Value')
        axs[i].tick_params(axis='x', rotation=45)
        axs[i].grid(True)

    # Título geral para a figura
    plt.suptitle('Metrics Boxplots per Component (Pasta)', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_image, dpi=300)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and visualize metrics from Prometheus.")
    parser.add_argument("start_end_timestamps", type=str, help="List of start and end UNIX timestamps as tuples. Example: '[(start1, end1), (start2, end2)]'")
    parser.add_argument("--output_csv", type=str, default="output.csv", help="Output CSV file name")
    parser.add_argument("--output_image", type=str, default="scientific_boxplots.png", help="Output image file name")

    args = parser.parse_args()

    # Converta a string do argumento em uma lista de tuplas
    start_end_timestamps = eval(args.start_end_timestamps)

    data = get_combined_metrics_data(start_end_timestamps, args.output_csv)
    if data is not None:
        generate_combined_boxplots_per_component(args.output_csv, args.output_image)
