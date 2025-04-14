import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

path = "./cuiaba/cuiabaTotal.CSV"
# ─────────────────────────────────────────────
# 1) LEITURA E LIMPEZA
# ─────────────────────────────────────────────
df = pd.read_csv(path, sep=';', dtype=str, na_values='-9999')

# normaliza DATA (2020/01/01 → 2020-01-01)
df['DATA'] = df['DATA'].str.replace('/', '-', regex=False).str.strip()

# normaliza HORA
df['HORA'] = df['HORA'].str.replace(' UTC', '', regex=False).str.strip()
mask = ~df['HORA'].str.contains(':')
df.loc[mask, 'HORA'] = (
    df.loc[mask, 'HORA']
      .str.zfill(4)
      .str.replace(r'(\d{2})(\d{2})', r'\1:\2', regex=True)
)

# corrige precipitação (vírgula→ponto, ".2"→"0.2")
def fix_prec(x: str):
    if pd.isna(x):
        return x
    x = x.strip()
    x = re.sub(r'^([,.])', r'0\1', x)
    x = x.replace(',', '.')
    return x

df['PRECIPITACAO'] = pd.to_numeric(df['PRECIPITACAO'].apply(fix_prec), errors='coerce')

# cria coluna datetime
df['Datetime'] = pd.to_datetime(
    df['DATA'] + ' ' + df['HORA'],
    format='%Y-%m-%d %H:%M',
    errors='coerce'
)

# mantém registros válidos
df = df.dropna(subset=['Datetime', 'PRECIPITACAO'])
df = df.set_index('Datetime').sort_index()

# ─────────────────────────────────────────────
# 2) AGREGAÇÃO DIÁRIA (série regular)
# ─────────────────────────────────────────────
daily = df['PRECIPITACAO'].resample('D').sum()
daily = daily.asfreq('D', fill_value=0)          # garante passo fixo
x = daily.values - daily.values.mean()           # remove média

# ─────────────────────────────────────────────
# 3) FFT E ESPECTRO DE POTÊNCIA
# ─────────────────────────────────────────────
N = len(x)
dt = 1.0                                         # 1 dia
freqs = np.fft.rfftfreq(N, d=dt)                 # ciclos por dia
fft_vals = np.fft.rfft(x)
power = np.abs(fft_vals) ** 2

# converte frequência → período (dias)
periods = np.where(freqs > 0, 1 / freqs, np.inf)

# identifica picos principais (exclui freq=0)
top_idx = np.argsort(power[1:])[::-1][:5] + 1
dominant_periods = periods[top_idx]
dominant_powers = power[top_idx]

# imprime resultados
print("Principais períodos detectados (dias) e potência relativa:")
for p, pw in zip(dominant_periods, dominant_powers):
    print(f"{p:8.1f} dias  |  potência = {pw:.2e}")

# ─────────────────────────────────────────────
# 4) PLOT DO ESPECTRO
# ─────────────────────────────────────────────
plt.figure(figsize=(8,4))
plt.plot(periods[1:], power[1:])
plt.xlim(0, 730)                                 # até 2 anos
plt.xlabel('Período (dias)')
plt.ylabel('Potência')
plt.title('Espectro de Potência (FFT)\nPrecipitação Diária - Cuiabá (2002‑2024)')
plt.grid(True)
plt.tight_layout()
plt.savefig("espectro_precipitacao_fft.png", dpi=150)
print("Gráfico salvo como espectro_precipitacao_fft.png")

