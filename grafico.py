# criando o arquivo CSV a partir do conteúdo que você forneceu e gerando gráficos com matplotlib
# instruções: este bloco escreve o CSV em /mnt/data, lê com pandas, cria 3 gráficos separados e salva PNGs.
# Também cria um README_Grafico.md com instruções de como colocar no GitHub.
import pandas as pd
import matplotlib.pyplot as plt
import os
from caas_jupyter_tools import display_dataframe_to_user

csv_text = """Implementacao,TamanhoTabela,TamanhoDados,Seed,FatorCarga,TempoInsercao(ms),TempoBusca(ms),Colisoes,Top1,Top2,Top3,MenorGap,MaiorGap,MediaGap,Status
Encadeamento,1009,100000,123456,99.11,105,465,4954012,129,130,133,0,0,0.000,OK
Sondagem Quadrática,1009,100000,123456,99.11,0,0,6799,0,0,0,0,1,0.001,CAPACIDADE_MAXIMA
Hash Duplo,1009,100000,123456,99.11,55,25,5375,0,0,0,0,0,0.000,CAPACIDADE_MAXIMA
Encadeamento,1009,1000000,234567,991.08,38175,47506,495557495,1077,1101,1112,0,0,0.000,OK
Sondagem Quadrática,1009,1000000,234567,991.08,0,0,5791,0,0,0,0,1,0.001,CAPACIDADE_MAXIMA
Hash Duplo,1009,1000000,234567,991.08,15,9,4818,0,0,0,0,0,0.000,CAPACIDADE_MAXIMA
Encadeamento,10007,100000,123456,9.99,13,19,500311,23,24,29,0,0,0.000,OK
Sondagem Quadrática,10007,100000,123456,9.99,19,16,594238,0,0,0,0,1,0.000,CAPACIDADE_MAXIMA
Hash Duplo,10007,100000,123456,9.99,306,182,87896,0,0,0,0,0,0.000,CAPACIDADE_MAXIMA
Encadeamento,10007,1000000,234567,99.93,3876,4668,49973171,134,138,141,0,0,0.000,OK
Sondagem Quadrática,10007,1000000,234567,99.93,1,2,569360,0,0,0,0,0,0.000,CAPACIDADE_MAXIMA
Hash Duplo,10007,1000000,234567,99.93,221,222,78296,0,0,0,0,0,0.000,CAPACIDADE_MAXIMA
"""

out_csv = "/mnt/data/resultados_hash_RA3.csv"
with open(out_csv, "w", encoding="utf-8") as f:
    f.write(csv_text)

# ler csv
df = pd.read_csv(out_csv)
# ajustar tipos numéricos
numeric_cols = ["TamanhoTabela","TamanhoDados","Seed","FatorCarga","TempoInsercao(ms)","TempoBusca(ms)","Colisoes","Top1","Top2","Top3","MenorGap","MaiorGap","MediaGap"]
for c in numeric_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# mostrar tabela para o usuário (visual)
display_dataframe_to_user("Resultados Hash (amostra)", df)

# Função auxiliar para mapear TamanhoDados para string legível (e manter ordem)
order = sorted(df["TamanhoDados"].unique())
xlabels = [str(int(x)) for x in order]

# 1) Gráfico: Tempo de Inserção vs TamanhoDados (por Implementacao) -- um gráfico único com linhas por Implementacao
plt.figure(figsize=(8,5))
for impl in df["Implementacao"].unique():
    sub = df[df["Implementacao"]==impl].sort_values("TamanhoDados")
    plt.plot(sub["TamanhoDados"], sub["TempoInsercao(ms)"], marker='o', label=impl)  # sem especificar cores
plt.xscale('log')
plt.xlabel("Tamanho do conjunto (log scale)")
plt.ylabel("Tempo de Inserção (ms)")
plt.title("Tempo de Inserção por Implementação (x Tamanho de Dados)")
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.3)
out1 = "/mnt/data/plot_tempo_insercao.png"
plt.savefig(out1, dpi=150, bbox_inches='tight')
plt.close()

# 2) Gráfico: Tempo de Busca vs TamanhoDados (por Implementacao)
plt.figure(figsize=(8,5))
for impl in df["Implementacao"].unique():
    sub = df[df["Implementacao"]==impl].sort_values("TamanhoDados")
    plt.plot(sub["TamanhoDados"], sub["TempoBusca(ms)"], marker='o', label=impl)
plt.xscale('log')
plt.xlabel("Tamanho do conjunto (log scale)")
plt.ylabel("Tempo de Busca (ms)")
plt.title("Tempo de Busca por Implementação (x Tamanho de Dados)")
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.3)
out2 = "/mnt/data/plot_tempo_busca.png"
plt.savefig(out2, dpi=150, bbox_inches='tight')
plt.close()

# 3) Gráfico: Colisões por Implementação vs TamanhoDados (eixo y em escala log devido à amplitude)
plt.figure(figsize=(8,5))
for impl in df["Implementacao"].unique():
    sub = df[df["Implementacao"]==impl].sort_values("TamanhoDados")
    plt.plot(sub["TamanhoDados"], sub["Colisoes"], marker='o', label=impl)
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Tamanho do conjunto (log scale)")
plt.ylabel("Colisões (escala log)")
plt.title("Colisões por Implementação (x Tamanho de Dados)")
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.3)
out3 = "/mnt/data/plot_colisoes.png"
plt.savefig(out3, dpi=150, bbox_inches='tight')
plt.close()

# criar README explicando como adicionar ao GitHub e embutir as imagens
readme_md = f\"\"\"# Resultados e Gráficos - Tabelas Hash (RA3)

Arquivos gerados:
- `resultados_hash_RA3.csv` — CSV com as métricas do experimento.
- `plot_tempo_insercao.png` — Gráfico: Tempo de Inserção vs Tamanho de Dados.
- `plot_tempo_busca.png` — Gráfico: Tempo de Busca vs Tamanho de Dados.
- `plot_colisoes.png` — Gráfico: Número de Colisões vs Tamanho de Dados.
- `plot_script.py` — (opcional) script usado para gerar esses gráficos.

## Como colocar no GitHub (passo a passo rápido)

1. Crie um novo repositório no GitHub (p.ex. `tabelas-hash-ra3`) pelo site do GitHub.
2. No seu projeto local (onde estão os arquivos), rode:
```bash
git init
git add resultados_hash_RA3.csv plot_tempo_insercao.png plot_tempo_busca.png plot_colisoes.png plot_script.py README.md
git commit -m \"Adicionar resultados e gráficos RA3\"
git remote add origin <URL_DO_REPOSITORIO>    # substitua <URL_DO_REPOSITORIO> pelo link do seu repo
git branch -M main
git push -u origin main
