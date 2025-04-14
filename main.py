import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

path = "./cuiaba/cuiabaTotal.CSV"

# Carregando os dados de precipitação (2002-2024) a partir do CSV
# Obs: -9999 e campos vazios indicam dados ausentes.
df = pd.read_csv(path, sep=';', na_values=['-9999', ''], decimal=',')

# Convertendo a coluna de precipitação para numérica (float) e tratando valores com vírgula
df['PRECIPITACAO'] = pd.to_numeric(df['PRECIPITACAO'], errors='coerce')

# Removendo possíveis espaços e padrões de hora "UTC" na coluna HORA
df['HORA'] = df['HORA'].str.strip().str.replace(' UTC', '')

# Padronizando formato da hora para HH:MM (adiciona ':' em horas que estejam no formato "HHMM")
mask = df['HORA'].str.len() == 4  # identifica entradas como "2300"
df.loc[mask, 'HORA'] = df.loc[mask, 'HORA'].str[:2] + ':' + df.loc[mask, 'HORA'].str[2:]

# Padronizando formato da data para YYYY-MM-DD (substitui '/' por '-' quando necessário)
df['DATA'] = df['DATA'].str.replace('/', '-')

# Combinando DATA e HORA em uma coluna datetime para facilitar agregação por dia
df['DATETIME'] = pd.to_datetime(df['DATA'] + ' ' + df['HORA'], format="%Y-%m-%d %H:%M", errors='coerce')

# Removendo linhas que não puderam ser convertidas em datetime (se houver)
df = df.dropna(subset=['DATETIME'])

# Definindo o índice do DataFrame como DATETIME e ordenando (caso não esteja em ordem temporal)
df = df.set_index('DATETIME').sort_index()

# Agregando a precipitação por dia (soma das 24 horas de cada dia)
daily_precip = df['PRECIPITACAO'].resample('D').sum()

# Aplicando Transformada Rápida de Fourier (FFT) na série diária de precipitação
precip_values = daily_precip.values
N = len(precip_values)                      # número de dias no registro
fft_vals = np.fft.fft(precip_values)        # FFT complexa
freqs = np.fft.fftfreq(N, d=1.0)            # frequências associadas (ciclos por dia)

# Calculando espectro de potência (magnitude ao quadrado da FFT)
power_spectrum = np.abs(fft_vals) ** 2

# Considerando apenas frequências positivas (a FFT de sinal real é simétrica;
# descartamos frequências negativas duplicadas)
mask_freq = freqs > 0
freqs_pos = freqs[mask_freq]               # frequências positivas (ciclos/dia)
power_pos = power_spectrum[mask_freq]      # potências correspondentes

# Convertendo frequências de ciclos/dia para ciclos/ano para facilitar a interpretação
freqs_per_year = freqs_pos * 365

# Identificando as principais frequências (maiores picos do espectro, excluindo 0 Hz)
dominant_indices = power_pos.argsort()[-5:][::-1]  # indices dos 5 maiores valores de potência
dominant_freqs = freqs_pos[dominant_indices]
dominant_periods = 1 / dominant_freqs  # período em dias correspondente a cada frequência dominante

# Exibindo os períodos dominantes identificados
print("Períodos dominantes (dias):", dominant_periods.round(1))
print("Frequências dominantes (ciclos/ano):", (dominant_freqs*365).round(2))

# Plotando o espectro de potência
plt.figure(figsize=(8, 5))
plt.plot(freqs_per_year, power_pos, color='blue')
plt.yscale('log')  # escala logarítmica para visualizar melhor picos menores
plt.xlim(0, 60)    # foco em até ~60 ciclos/ano (período mínimo ~6 dias, cobre variação semanal)

# Rótulos e título do gráfico
plt.xlabel('Frequência (ciclos por ano)')
plt.ylabel('Potência Espectral')
plt.title('Espectro de Potência da Precipitação Diária - Cuiabá (2002-2024)')

# Linhas verticais indicando algumas frequências de interesse (1 ciclo/ano, 2 ciclos/ano, etc.)
plt.axvline(1, color='red', linestyle='--', alpha=0.7)    # ~365 dias
plt.axvline(2, color='orange', linestyle='--', alpha=0.5) # ~180 dias
plt.axvline(12, color='green', linestyle='--', alpha=0.5) # ~30 dias (aprox. 12 ciclos/ano)
plt.axvline(52, color='purple', linestyle='--', alpha=0.5) # ~7 dias (aprox. 52 semanas/ano)

# Anotações de texto para destacar os períodos
plt.text(1.5, power_pos.max(), '≈ 365 dias', color='red', va='center')
plt.text(2.5, 2e6, '≈ 180 dias', color='orange')
plt.text(13, 1e6, '≈ 30 dias', color='green')
plt.text(53, 3e5, '7 dias', color='purple')

plt.tight_layout()
plt.savefig('espectro_cuiaba.png')
plt.show()
