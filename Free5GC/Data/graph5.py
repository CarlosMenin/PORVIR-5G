import os
import pandas as pd
import matplotlib.pyplot as plt

folder = os.getcwd()

boxplot_data = []
labels = []

for nome_arquivo in os.listdir(folder):
    if nome_arquivo.endswith(".csv"):
        if "div" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[4]}ms,\nDividing by {nome_arquivo.split("_")[5]}\nEvery {nome_arquivo.split("_")[6]} Connections'
        elif "dec" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[4]}ms,\nDecreased by {nome_arquivo.split("_")[5]}\nEvery {nome_arquivo.split("_")[6]} Connections'
        else:
            title = f'Parallel Connection Test:\nInterval of {nome_arquivo.split("_")[3]}ms'
        labels.append(title)
        data = pd.read_csv(os.path.join(folder, nome_arquivo))
        connection_times = data['DataPlaneReady'].values
        boxplot_data.append(connection_times)

plt.figure(figsize=(12, 8))
plt.boxplot(boxplot_data, labels=labels)
plt.title('Connection Times', fontsize=16)
plt.xlabel('Test Configurations', fontsize=14)
plt.ylabel('Time to Connection (ms)', fontsize=14)
plt.xticks(rotation=0, ha='center', fontsize=12)
plt.margins(x=0.05)  # Add a small margin on each side of the x-axis to avoid label cutoff
plt.grid(True)
plt.tight_layout()

plt.savefig('box_plot_all_tests.png', dpi=300, bbox_inches='tight')
plt.show()

