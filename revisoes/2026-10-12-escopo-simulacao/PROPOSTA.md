# Proposta: comparativo em simulação — piloto humano × controle clássico × aprendizado de máquina

Plano de execução completo, com fases, datas e todas as decisões: `PLANO.md` (mesma pasta). Onde os dois divergirem,
vale o `PLANO.md` (ex.: título muda, seção ROS2 sai, seguidor de gap entra).

Estado: **proposta, não aplicada.** Nenhum `.tex` nem código foi alterado. Versão 2, de 12/10/2026: substitui a
versão 1 (escopo só em simulação, sem piloto humano).

## Decisão

O estudo passa a ser um comparativo, no mesmo simulador e sob o mesmo avaliador, entre três tipos de piloto:

| Piloto | O que é | Situação |
|---|---|---|
| Humano | Pessoa dirigindo por joystick, em tempo real | **A construir** |
| Controle clássico | Especialista *pure pursuit* (E1); opcionalmente o seguidor de parede | Pronto (E1: 59,000 s, 50/50 voltas) |
| Aprendizado de máquina | Imitação TinyLidarNet (E2) e reforço residual SAC (E3) | Pronto (E2: 60,050 s; E3: 52,525 s, 91/92 voltas) |

Decisões tomadas em 12/10/2026:
- **Pilotos humanos:** os autores (Gustavo e Julio) **e voluntários**.
- **Vista do humano:** as duas condições, pista inteira vista de cima e só os pontos do LiDAR.
- **Modelo físico:** sai **por completo** da dissertação e do TG. A Raspberry Pi 4B queimou e não será substituída. O
  material do carro continua nos registros do projeto, marcado como descontinuado para o TG (feito em 12/10/2026 em
  `f1tenth_code/car/README.md`, `f1tenth_code/STATUS.md`, `f1tenth_code_rasp/README.md` e
  `Graduacao/README.md`).

## Enquadramento nas normas

- **Permitido:** a Res. ConCECS 17/2013, art. 2º, II, aceita TG de "caráter teórico ou teórico/prático/empírico".
  Comparar métodos em simulação é aceito na prática da IAR (há temas recentes como "abordagens clássicas e Aprendizado
  por Reforço" e "goleiro robótico simulado").
- **Tema:** continua sendo pilotagem autônoma F1TENTH, no perfil Robótica do PPC. O título pode ficar.
- **Metodologia:** muda mais que na versão 1, porque entra um experimento novo com pessoas. As fichas do orientador
  perguntam "mudança significativa no tema?" e "na metodologia?". **O Filipe precisa concordar antes.** O FAQ (item 5)
  aceita adaptações que não mudem radicalmente o tema.
- **Pesquisa com pessoas (obrigatório resolver antes de coletar voluntários):** como haverá voluntários, perguntar ao
  orientador, antes de qualquer coleta, se o estudo precisa passar pelo Comitê de Ética em Pesquisa da UFABC
  (Res. CNS 466/2012 e 510/2016). Se precisar, a submissão pela Plataforma Brasil leva semanas e tem de começar
  **ainda em 2026**. Em qualquer caso: termo de consentimento assinado, dados anônimos (piloto identificado por código,
  sem nome), e nenhuma informação pessoal além do que o protocolo pedir (ex.: experiência prévia com jogos de corrida).
  As voltas dos autores podem ser coletadas antes, sem esperar essa resposta.

## O que já existe e o que falta construir

Já existe em `f1tenth_code`:
- `research/f1tenth_research/rollout.py`: `evaluate()` avalia qualquer objeto com a interface `Policy`
  (`policy(obs, info) -> ação`) e devolve conclusão de volta, tempos por *seed* e intervalos de confiança.
- Ambiente, colisão e randomização de atrito, largada e ruído (`env.py`, `collision.py`), usados nas etapas E1–E3.
- Joystick para o simulador ROS (`src/Joy_converter`) e teleoperação por teclado no `gym_bridge`
  (`kb_teleop: True`), que servem de referência de mapeamento de eixos (`max_speed` 7,0 m/s, `max_angle` 0,32 rad).

Falta:
1. **`HumanPolicy`**: uma `Policy` que, a cada passo, lê o joystick (ex.: `pygame.joystick`) e devolve
   `[esterço, velocidade]` com os mesmos limites de saturação dos outros pilotos, e segura o passo para correr em tempo
   real (1×).
2. **Visualização**: o ambiente de avaliação não renderiza (`render_modes: []`). É preciso uma janela de cima (mapa da
   pista + pose do carro), senão a pessoa não tem o que ver.
3. **Protocolo de sessão**: aquecimento, número de voltas cronometradas, registro de cada sessão como *run* com
   proveniência (mesmo padrão dos portões existentes).
4. **Critérios congelados antes da coleta**, como nas etapas E1–E3 (o que conta como volta válida, quantas voltas,
   quais pistas, com ou sem randomização).

## Desenho do experimento (pontos que precisam ser decididos e declarados)

1. **Mesma pista, mesmo avaliador.** Spielberg como pista principal; as pistas de generalização são opcionais para o
   humano (o humano não "treina" numa pista e "testa" em outra do mesmo modo que a rede).
2. **Informação desigual.** O humano vê a pista inteira de cima; as políticas veem só o LiDAR 2D. Declarar como
   limitação, ou dar ao humano uma vista restrita (só os pontos do LiDAR), o que torna a comparação mais justa. Sugestão:
   as duas condições, se o tempo permitir.
3. **Aprendizado do humano.** Registrar a curva de tempo por volta ao longo das tentativas e comparar a melhor volta e a
   mediana das últimas N, não só a melhor.
4. **Randomização.** E2 e E3 foram medidas com randomização de atrito, largada e ruído; o E1 não. Escolher uma condição
   comum para os três tipos de piloto, ou declarar a assimetria (a monografia já faz isso para E1 × E3).
5. **Métricas:** taxa de conclusão de volta, tempo de volta (mediana e melhor), colisões, e suavidade do comando
   (variação do esterço), que é onde humano e máquina costumam diferir.
6. **Pilotos:** quantos, e se são só os autores. Com 1 ou 2 pilotos o resultado é um estudo de caso, e o texto deve dizer
   isso.
7. **Extra opcional:** usar as voltas humanas como demonstrações para treinar a imitação (imitação de humano ×
   imitação do especialista). Só se sobrar tempo.

## 1. Novos objetivos — `capitulos/introducao.tex` (substitui a seção Objetivos, linhas ~88–112)

```latex
\section*{Objetivos}\label{sec:objetivos}
\addcontentsline{toc}{section}{Objetivos}

De modo geral, este trabalho tem como objetivo comparar, num mesmo simulador da
plataforma F1TENTH e sob os mesmos critérios de avaliação, três formas de
pilotar um veículo de corrida em escala 1:10: um piloto humano, um controlador
clássico e políticas obtidas por aprendizado de máquina. Para tanto, são
perseguidos os seguintes objetivos específicos:
\begin{enumerate}
    \item Implementar e avaliar em simulação controladores clássicos: o
          especialista \textit{pure pursuit}, usado também como fonte de
          demonstrações, e um seguidor de gap reativo;
    \item Treinar uma política de imitação que dispense pose global e
          refiná-la por aprendizado por reforço residual, avaliando-as sob
          critérios fixados antes da medição;
    \item Desenvolver uma interface de pilotagem humana no mesmo simulador e
          coletar voltas de pilotos humanos sob protocolo definido antes da
          coleta;
    \item Comparar os três tipos de piloto quanto a taxa de conclusão de volta,
          tempo de volta, colisões e suavidade do comando, com o piloto humano
          em duas condições de informação: a pista inteira vista de cima e
          apenas as leituras do LiDAR, as mesmas que as políticas recebem.
\end{enumerate}

\subsection*{Delimitação do escopo}

O plano inicial deste trabalho previa a construção de um veículo em escala e
experimentos com ele. Essa frente foi descontinuada após a falha da unidade de
processamento embarcada, e o trabalho foi redefinido, em comum acordo com o
orientador, como um estudo comparativo inteiramente em simulação. Nenhum
resultado deste texto depende de hardware.
```

A delimitação não dá a data nem detalhes do carro, porque o modelo físico sai do texto inteiro. Se o orientador
preferir, ela pode ser ainda mais curta ou ir para a Metodologia.

## 2. O que sai da dissertação (remoção do modelo físico)

Levantamento feito em 12/10/2026 sobre a árvore de trabalho. Menções ao hardware por capítulo: conclusão 55,
construção do veículo 69, resultados 43, metodologia 37, estado da arte 28, regulamentação 26, ferramentas 14,
introdução 8.

| Onde | O que fazer |
|---|---|
| `dissertacao.tex`, linha 196 | Tirar `\include{capitulos/construcao_veiculo}`. O arquivo fica no repositório, fora do texto |
| `regulamentacao.tex` (cap. inteiro) | Hoje trata das exigências do carro físico (plataforma, sensores, segurança, inspeção). **Proposta:** remover o capítulo e levar 1–2 parágrafos sobre o formato *time trial* para o Estado da Arte, porque é o formato que a comparação de tempo de volta imita |
| `consideracoes.tex` (cap. "Considerações finais", 35 linhas) | Fala das regras da categoria. Remover junto com a regulamentação, ou fundir no texto acima |
| `proposta.tex`, § "Controle no veículo físico" (linha 133) | Remover |
| `metodologia_validacao.tex`, § "Ponte sim-to-real: adaptador de observação, guarda de comando…" (linha 918) | Remover. Conferir `SPEC-CAR-*` citados no resto do capítulo |
| `metodologia_validacao.tex`, § "O escopo é a simulação, e a Camada F é o contêiner" (linha 1346) | Reescrever: o escopo agora é só simulação por decisão, não por limitação |
| `resultados.tex`, § "Sensibilidade ao contrato de observação do sensor real" (`sec:res-s2r`, linhas 693–999, inclui o retreino E4.1) | **Remover.** O experimento roda em simulação, mas só existe para medir a distância até o sensor do carro. Sem o carro, perde a razão de estar no texto. Fica no repositório como registro |
| `resultados.tex`, § "A política dirigindo no contêiner ROS2" (`sec:res-deploy`) | **Decisão em aberto.** Não depende de hardware (é tempo real contra o simulador). Pode ficar como resultado de engenharia, ou sair para enxugar |
| `estadodaarte.tex`, § "Transferência simulação-realidade" (`sec:arte-s2r`, linha 622) | Reduzir a um parágrafo de contexto, ou remover |
| `estadodaarte.tex`, § "A plataforma F1TENTH" e "Do veículo de competição ao modelo em escala" | Manter, mas como contexto da plataforma e do simulador, sem o carro deste trabalho |
| `ferramentas.tex`: "Integração de Sensores e Atuadores para F1TENTH", "Considerações de Tempo Real", "Mapeamento da pista real: não realizado", trechos de odometria de rodas | Remover ou reduzir ao que o simulador usa |
| `introducao.tex` | Trocar objetivos (seção 1 acima) e tirar a promessa do carro na motivação |
| `conclusao.tex` | Reescrever a abertura, a tabela de objetivos (4 linhas), os parágrafos por objetivo, "Trabalhos Futuros" (o carro deixa de ser "a fase seguinte já especificada"; no máximo uma linha dizendo que a validação em hardware é possível) e a "Consideração final" (que hoje cita o veículo construído) |
| `pretextual/resumos.tex` | Reescrever resumo e abstract para o comparativo |
| `bibliografia.bib` | Depois dos cortes, remover entradas que ficarem sem citação (ex.: datasheets) |
| `extras/dados.tex` | `\data{}` e "Título de Engenheiro(a)" |

## 3. O que entra no texto

| Parte | Mudança |
|---|---|
| Introdução | Objetivos acima e justificativa: por que comparar com humano (referência de desempenho conhecida, leitura do que a rede aprendeu) |
| Estado da arte | Seção curta sobre comparações entre pilotos humanos e controladores autônomos em corrida |
| Proposta / Metodologia | Nova seção: interface humana, protocolo de sessão, as duas condições de vista, critérios congelados, termo de consentimento e anonimização |
| Resultados | Nova seção com as voltas humanas e uma tabela comparativa única (humano em cada vista, E1, E2, E3) |
| Conclusão | Tabela com os 4 objetivos novos |

## 4. Riscos

- **Prazo.** O TG III é em 2027.1 (aulas de 01/02 a 07/05/2027). A interface humana, a coleta e uma seção nova de
  resultados são trabalho novo; o resto já existe. Começar a interface antes de fevereiro.
- **Comparação injusta** se o humano vir a pista inteira e a rede só o LiDAR. Declarar ou equalizar (item 2 do desenho).
- **Amostra pequena.** Com 1 ou 2 pilotos, não generalizar para "humanos"; falar em "pilotos humanos deste estudo".
- **Orientador e coautor.** Sem o acordo do Filipe e do Julio, não aplicar.

## Decisões em aberto

1. Resposta do orientador sobre o Comitê de Ética (bloqueia a coleta com voluntários, não a dos autores).
2. Condição de randomização comum aos três pilotos.
3. Se a seção de *deploy* no contêiner ROS2 (`sec:res-deploy`) fica.
4. Se o capítulo de regulamentação sai inteiro ou vira 1–2 parágrafos no Estado da Arte.
5. Acordo do Filipe e do Julio com o novo escopo.

## Já decidido

- Pilotos: autores e voluntários. Vista: as duas condições. Modelo físico: fora da dissertação e do TG, marcado como
  descontinuado nos registros do projeto (12/10/2026).
