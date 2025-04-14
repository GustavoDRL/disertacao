# Dissertação [Placeholder: Seu Título Aqui]

## Descrição

[Placeholder: Adicione uma breve descrição do seu projeto de dissertação aqui.]

## Estrutura do Projeto

- `main.tex`: Arquivo principal para compilação.
- `dissertacao.tex`: Arquivo raiz da dissertação (provavelmente incluído pelo `main.tex`).
- `bibliografia.bib`: Arquivo BibTeX com as referências bibliográficas.
- `capitulos/`: Diretório contendo os arquivos `.tex` de cada capítulo.
- `pretextual/`: Diretório contendo os arquivos dos elementos pré-textuais (capa, folha de rosto, resumo, etc.).
- `postextual/`: Diretório contendo os arquivos dos elementos pós-textuais (apêndices, anexos, etc.).
- `figs/`: Diretório para armazenar as figuras e imagens.
- `manuais/`: [Placeholder: Descreva o conteúdo deste diretório, se aplicável].
- `extras/`: [Placeholder: Descreva o conteúdo deste diretório, se aplicável].

## Como Compilar

[Placeholder: Descreva os passos para compilar o documento LaTeX. Exemplo:]

1.  Certifique-se de ter uma distribuição LaTeX instalada (como TeX Live, MiKTeX).
2.  Use um editor LaTeX ou a linha de comando para compilar o arquivo `main.tex`. Geralmente, a sequência de compilação pode exigir múltiplas passagens e o uso do BibTeX/Biber:
    ```bash
    pdflatex main.tex
    bibtex dissertacao # Ou o nome base do seu arquivo .aux se for diferente
    pdflatex main.tex
    pdflatex main.tex
    ```
    Alternativamente, ferramentas como `latexmk` podem simplificar o processo:
    ```bash
    latexmk -pdf main.tex
    ```

## Dependências

[Placeholder: Liste quaisquer pacotes LaTeX especiais ou fontes externas necessárias.]

## Contribuição

[Placeholder: Se aplicável, descreva como outros podem contribuir.]

## Licença

[Placeholder: Especifique a licença do seu trabalho, se houver.]
