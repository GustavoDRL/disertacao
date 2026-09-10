# Desenvolvimento de um Veículo Autônomo de Corrida Conforme as Regulamentações da Categoria "F1TENTH"

## Descrição

Trabalho de Graduação do Programa de Graduação em Engenharia da
Instrumentação Automação e Robótica (UFABC), sobre o desenvolvimento de um
veículo autônomo de corrida na categoria F1TENTH, incluindo a construção do
veículo e a avaliação, em simulação, de controladores clássicos e de
aprendizado (imitação e reforço residual) para pilotagem autônoma.

## Estrutura do Projeto

- `dissertacao.tex`: arquivo raiz do documento (compila diretamente, não há
  `main.tex`).
- `bibliografia.bib`: arquivo BibTeX com as referências bibliográficas.
- `capitulos/`: capítulos do texto (introdução, ferramentas, construção do
  veículo, regulamentação, considerações, proposta, resultados, conclusão).
- `pretextual/`: elementos pré-textuais (capa, folha de rosto, ficha
  catalográfica, folha de assinaturas, agradecimentos, epígrafe, resumo e
  abstract).
- `postextual/`: elementos pós-textuais (apêndices, anexos).
- `extras/`: dados de identificação do trabalho e configurações do abnTeX2
  (citações, aparência do PDF).
- `figs/`: figuras e imagens usadas no documento.

## Como Compilar

Requer uma distribuição LaTeX (TeX Live ou MiKTeX) com o pacote `abntex2` e
`latexmk`. A partir da raiz do repositório:

```bash
latexmk -pdf dissertacao.tex
```

Para limpar os arquivos auxiliares gerados pela compilação:

```bash
latexmk -c
```

## Estado editorial

A versão de trabalho omite ficha catalográfica, folha de aprovação e agradecimentos
até que seus conteúdos reais estejam disponíveis. Não representa uma versão
aprovada pela banca. O capítulo de proposta descreve a organização atual do
workspace `f1tenth_code`, revisada em 10/09/2026; os resultados experimentais
continuam vinculados às execuções e versões indicadas no capítulo de resultados.
