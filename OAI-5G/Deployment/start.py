import subprocess
import time

def aplicar_manifesto(caminho_do_arquivo):
    comando = f'kubectl apply -f {caminho_do_arquivo}'
    processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    saida, erro = processo.communicate()
    
    if processo.returncode == 0:
        print(f'Sucesso! O comando foi executado:\n{saida.decode("utf-8")}')
    else:
        print(f'Erro ao executar o comando:\n{erro.decode("utf-8")}')
    
    time.sleep(45)

arquivos_manifesto = [
    'nrf.yaml',
    'mysql.yaml',
    'udr.yaml',
    'udm.yaml',
    'ausf.yaml',
    'amf.yaml',
    'smf.yaml',
    'upf.yaml'
]

for arquivo in arquivos_manifesto:
    aplicar_manifesto(arquivo)

