# Comparativo humano × clássico × aprendizado de máquina

Gerado em 2026-10-13 08:08:19. Os demais arquivos desta pasta dependem apenas dos runs listados abaixo.

## Arquivos

- `comparativo.json`: todas as linhas, o protocolo, os runs usados, os humanos excluídos (com motivo) e os avisos.
- `comparativo.csv`: as mesmas linhas, uma por piloto automático e uma por (piloto humano, vista), mais as agregadas por grupo e vista (melhor, mediana e pior piloto).
- `tabela_comparativo.tex`: tabela LaTeX (`tabular` com `\hline`) pronta para `\input`; números com vírgula decimal e `pendente` onde falta dado.
- `perfil_velocidade`: velocidade média por faixa de 1 m de `s`, por piloto.
- `esterco_vs_tempo`: taxa de esterço média × tempo de cada volta completa.
- `curva_aprendizado`: tempo por volta, na ordem, do treino e das sessões.
- `trajetorias_curva`: trajetórias da volta de tempo mediano de cada piloto no trecho de maior curvatura da raceline (±15 m de `s`).
  Cada figura existe em PDF e PNG.

## Runs de origem

- Pure pursuit (E1): `cmp_Spielberg_20261012-225730_0dda764_11e48d`
- Imitação (E2): `cmp_Spielberg_20261012-225730_0dda764_f7b67f`
- Resíduo SAC (E3): `cmp_Spielberg_20261012-225731_0dda764_00a206`
- Disparity Extender: `cmp_Spielberg_20261013-080135_8d57af8_e562f9`
- Seguidor de gap: `cmp_Spielberg_20261013-080135_8d57af8_3a64c2`

Humanos incluídos: nenhum (linhas pendentes).
