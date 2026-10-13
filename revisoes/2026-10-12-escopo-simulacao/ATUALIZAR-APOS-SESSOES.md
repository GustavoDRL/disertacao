# Atualizar a monografia depois das sessões humanas

Escrito em 13/10/2026, com os pilotos automáticos medidos e nenhuma sessão humana feita. O texto de resultados,
discussão, conclusão e resumos já está escrito; o que depende dos humanos está marcado com a macro
`\pendentehumano{...}` (definida em `dissertacao.tex`), que aparece no PDF em negrito como
**[aguardando sessões humanas: ...]**. Este roteiro diz como trocar cada marca pelo dado.

## 1. Regenerar tabela e figuras

Na worktree de execução do `f1tenth_code` (hoje `TG/.worktrees/cmp-execucao`, branch do comparativo), com a árvore
limpa e os runs humanos já gravados em `research/runs/`:

```bash
cd /home/disney/Documents/repos/UFABC/TG/.worktrees/cmp-execucao/research
git status --short                      # deve sair vazio
.venv/bin/python -m f1tenth_research cmp tabela
```

A saída vai para `research/runs/comparativo/`: `comparativo.json`, `comparativo.csv`, `tabela_comparativo.tex`,
`LEIA-ME.md` e as figuras `perfil_velocidade`, `esterco_vs_tempo`, `curva_aprendizado` e `trajetorias_curva`, cada
uma em PDF e PNG.

Antes de copiar, conferir em `comparativo.json`:

- `runs.humanos`: um run por (piloto, vista) que deveria entrar;
- `humanos_excluidos`: cada exclusão com motivo (protocolo, `protocol_hash`, sessão incompleta, duplicado);
- `avisos`: vazio, ou cada aviso entendido;
- `runs.automaticos`: os mesmos cinco runs de hoje (`…_11e48d`, `…_f7b67f`, `…_00a206`, `…_e562f9`, `…_3a64c2`). Se
  algum mudou, os números dos pilotos automáticos citados no texto precisam ser revistos também.

## 2. Copiar para a monografia

No checkout principal da monografia (branch `main`):

```bash
SRC=/home/disney/Documents/repos/UFABC/TG/.worktrees/cmp-execucao/research/runs/comparativo
DST=/home/disney/Documents/repos/UFABC/TG/disertacao

# resumo versionado (fonte dos números do texto); varreduras/ não muda
cp "$SRC"/{LEIA-ME.md,comparativo.json,comparativo.csv,tabela_comparativo.tex} "$DST"/resultados-comparativo/
cp "$SRC"/*.pdf "$SRC"/*.png "$DST"/resultados-comparativo/

# o que o LaTeX lê
cp "$SRC"/tabela_comparativo.tex "$DST"/tabelas/tabela_comparativo.tex
cp "$SRC"/{perfil_velocidade,esterco_vs_tempo,curva_aprendizado,trajetorias_curva}.pdf "$DST"/figs/comparativo/
```

Depois, versione também o relatório de cada run usado pela tabela (automáticos e humanos), para que todo número do
texto continue com fonte. O `cmp tabela` reescreve o `LEIA-ME.md` e apaga a linha que descreve esta pasta; a última
linha do comando a devolve.

```bash
RUNS=/home/disney/Documents/repos/UFABC/TG/.worktrees/cmp-execucao/research/runs
python3 - "$SRC/comparativo.json" <<'PY' | while read -r rid; do
import json, sys
r = json.load(open(sys.argv[1]))["runs"]
ids = list(r["automaticos"].values())
ids += [h if isinstance(h, str) else h.get("run_id") for h in r["humanos"]]
print("\n".join(i for i in ids if i))
PY
  mkdir -p "$DST/resultados-comparativo/runs/$rid"
  for f in config.yaml eval_report.json metrics.json treino.json timing.json; do
    [ -f "$RUNS/$rid/$f" ] && cp "$RUNS/$rid/$f" "$DST/resultados-comparativo/runs/$rid/"
  done
done
echo '- `runs/<run_id>/`: `config.yaml`, `eval_report.json`, `metrics.json` (e, nos humanos, `treino.json` e `timing.json`) de cada run da tabela, para conferir os números do texto que não estão no resumo agregado.' >> "$DST/resultados-comparativo/LEIA-ME.md"
```

`tabelas/tabela_comparativo.tex` é gerado: não editar. Com várias linhas humanas (uma por piloto e vista, mais as
agregadas por grupo e vista), conferir no PDF se a tabela ainda cabe na página. Se não couber em altura, envolver o
`\input{tabelas/tabela_comparativo}` (em `capitulos/resultados.tex`, Seção "Tabela comparativa e métricas") em
página paisagem, sem mexer no arquivo gerado.

## 3. Trocar cada `\pendentehumano`

Os números de linha são os de 13/10/2026 e mudam à medida que o texto for preenchido. Rodar antes
`grep -rn "pendentehumano" capitulos pretextual` e seguir a ordem abaixo, de cima para baixo em cada arquivo.
Todo número escrito sai de `resultados-comparativo/` (nunca de memória nem do terminal).

| # | Arquivo:linha | Contexto | O que escrever |
|---|---|---|---|
| 1 | `capitulos/resultados.tex:835` | Seção "Pilotos humanos", 1º parágrafo | Quantos autores e voluntários participaram, por grupo e experiência em jogos de corrida; sessões excluídas e o motivo de cada uma (de `humanos_excluidos`) |
| 2 | `capitulos/resultados.tex:839` | "Resultado por piloto e vista", pista inteira | Por piloto: voltas completas/tentadas, colisões, mediana e melhor volta; autores separados dos voluntários |
| 3 | `capitulos/resultados.tex:841` | idem, só LiDAR | Os mesmos campos na vista só LiDAR |
| 4 | `capitulos/resultados.tex:845` | "Tempo real" | Atraso médio, percentil 99 e passos fora do prazo de 0,05 s, por sessão (de `timing.json` de cada run humano) |
| 5 | `capitulos/resultados.tex:849` | Leitura da Figura `fig:cmp_curva` | Tendência no treino, diferença entre a 1ª e a 3ª sessão, mudança na troca de vista |
| 6 | `capitulos/resultados.tex:862` | "Faixa do grupo e posição das políticas" | Melhor, mediana e pior piloto por vista (linhas agregadas do CSV) e onde E1, E2, E3 e Disparity Extender caem em relação a essa faixa |
| 7 | `capitulos/resultados.tex:866` | "Comparação entre as vistas" | Por piloto, a diferença de conclusão e de mediana entre pista inteira e só LiDAR |
| 8 | `capitulos/resultados.tex:904` | `tab:res_sintese`, linha "Humano, pista inteira" | Trocar o `\multicolumn{5}` por `--- & --- & --- & <faixa da volta> & <faixa da conclusão>` (faixa = melhor–pior, ou mediana [melhor; pior]; dizer qual na legenda) |
| 9 | `capitulos/resultados.tex:907` | idem, "Humano, só LiDAR" | Idem para a vista só LiDAR |
| 10 | `capitulos/resultados.tex:1151` | Discussão, "A comparação com os pilotos humanos" | Posição de cada política diante da faixa do grupo, por vista, com a leitura fixada no parágrafo (só LiDAR = informação equivalente; pista inteira = mais informação) |
| 11 | `capitulos/resultados.tex:1156` | Discussão, humano só LiDAR × seguidor de gap | Se e quanto os humanos na vista só LiDAR completaram voltas que o seguidor de gap não completa |
| 12 | `capitulos/resultados.tex:1158` | Discussão, suavidade | Taxa de esterço e desvio da linha de corrida dos humanos diante das políticas |
| 13 | `capitulos/resultados.tex:1181` | Subseção "Síntese" | Uma frase: posição das políticas diante da faixa humana em cada vista |
| 14 | `capitulos/conclusao.tex:185` | Objetivo 3 | Pilotos coletados (autores e voluntários), sessões completas e excluídas, situação do Comitê de Ética |
| 15 | `capitulos/conclusao.tex:192` | Objetivo 4 | Faixa do grupo por vista e posição de cada política |
| 16 | `capitulos/conclusao.tex:208` | "O que fica dito com precisão" | A afirmação central sobre humano e máquina, por vista |
| 17 | `capitulos/conclusao.tex:288` | "Consideração final" | Uma frase com o resultado humano |
| 18 | `pretextual/resumos.tex:32` | Resumo | Uma frase com o resultado humano em cada vista |
| 19 | `pretextual/resumos.tex:71` | Abstract | A mesma frase, em inglês |

## 4. Trechos sem a macro que também mudam

A coleta muda a situação descrita nestes pontos, que não têm `\pendentehumano` porque hoje estão corretos:

- `capitulos/resultados.tex`, abertura do capítulo: a frase "As sessões dos pilotos humanos ainda não foram
  realizadas; os pontos do texto que dependem delas estão marcados como pendentes [...]".
- `capitulos/resultados.tex`, Seção "Pilotos humanos": "As linhas humanas da Tabela [...] estão reservadas e ainda
  vazias."
- `capitulos/resultados.tex`, Seção "Procedência" do comparativo: acrescentar os runs humanos (lista de
  identificadores e, se couber, linhas na `tab:res_cmp_proveniencia`).
- `capitulos/conclusao.tex`, parágrafo de abertura ("Faltam as sessões com os pilotos humanos [...]").
- `capitulos/conclusao.tex`, `tab:conc_objetivos`: coluna Situação dos objetivos 3 e 4 (hoje "em parte") e a
  legenda ("A situação dos objetivos 3 e 4 é a desta versão, anterior às sessões humanas").
- `capitulos/conclusao.tex`, "O que fica dito com precisão": a contagem "dois estão atingidos e dois em parte".
- `capitulos/conclusao.tex`, "Consideração final": "cuja parte humana depende de coleta ainda por fazer".
- `capitulos/conclusao.tex`, Objetivo 3: a frase sobre a dependência do Comitê de Ética.
- Se os voluntários não entrarem (parecer do CEP fora do prazo), declarar isso no Objetivo 3 e nos Trabalhos Futuros.

## 5. Conferir e fechar

```bash
cd /home/disney/Documents/repos/UFABC/TG/.worktrees/texto-resultados
grep -rn "pendentehumano" capitulos pretextual          # deve sair vazio
latexmk -pdf -interaction=nonstopmode dissertacao.tex > /dev/null 2>&1; echo exit=$?
grep -c -E "undefined" dissertacao.log                 # 0
grep -a "Overfull" dissertacao.log                     # conferir tabela e figuras
grep -a "Output written" dissertacao.log
```

Com o grep vazio, a definição de `\pendentehumano` em `dissertacao.tex` pode ser removida. Conferir no PDF a
Tabela "Comparativo entre pilotos [...]" e a Figura "Curva de aprendizado [...]", que hoje mostra o aviso
"aguardando sessões humanas".
