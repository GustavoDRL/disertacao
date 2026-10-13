# Plano: TG como comparativo em simulação (humano × clássico × aprendizado de máquina)

Montado em 12/10/2026 a partir de: inventário do código `f1tenth_code/research/`, inventário da monografia
(`TG/disertacao`), `PROPOSTA.md` (mesma pasta) e respostas do aluno. **Nada foi executado ainda.** Datas são metas;
as do TG III 2027.1 são estimativas pelo calendário de 3Q2026.

## 0. Decisões registradas

| Tema | Decisão |
|---|---|
| Entrega | TG III em **2027.1** (pedido na 1ª semana: 01–05/02/2027) |
| Pilotos | **Clássicos:** pure pursuit (E1) + **seguidor de gap** (a portar). **ML:** imitação (E2) + RL residual (E3). **Humanos:** Gustavo, Julio e **3 a 5 voluntários** |
| Carro físico | Fora da monografia e do TG; marcado como descontinuado nos registros (feito em 12/10/2026) |
| Orientador | Recebe a mudança **já formatada** (ver Fase 7). Coleta com voluntários fica bloqueada até ele responder sobre o Comitê de Ética |
| Divisão com o Julio | Sem divisão: o plano é executado por você |
| Código novo | Dentro de `f1tenth_code/research/` (mesmo `evaluate`, testes e registro de runs) |
| Controle | Joystick que você já tem; **analógico esquerdo = esterço, gatilho direito = velocidade** (solto 1 m/s, fundo 8 m/s) |
| Limites do humano | **Iguais aos das políticas:** esterço ±0,4189 rad, velocidade 1–8 m/s, sem parar nem ré, mesmo atraso de esterço de 100 ms |
| Visualização | Janela própria em **pygame**, duas vistas: **pista inteira** (mapa visto de cima) e **só LiDAR** (pontos do scan, carro fixo no centro apontando para cima, sem rastro) |
| HUD | Velocidade atual, tempo da volta atual e da última, sessão e volta (ex.: "sessão 2 · volta 3/5") |
| Randomização | **Todos os pilotos com randomização** (atrito, largada na raceline, ruído de LiDAR), como E2/E3 oficiais |
| Pista | Só **Spielberg** |
| Protocolo humano | Por vista: **10 min de treino** (gravado, não conta) + **3 sessões × 5 voltas**; cada sessão é uma seed |
| Colisão | **Encerra a sessão** (mesma regra das políticas). Voltas não feitas contam como não tentadas |
| Ordem das vistas | **Sempre pista inteira primeiro** (declarar o efeito de aprendizado a favor da vista só-LiDAR) |
| Sessões | Presenciais, no seu computador e com o mesmo joystick. Sem remoto por enquanto |
| Métricas | Conclusão de volta (Wilson), tempo de volta (mediana e melhor), colisões, **suavidade do esterço**, **desvio da raceline**, **perfil de velocidade**, **curva de aprendizado humano** |
| Estatística | **Estudo de caso descritivo**: tabela por piloto e faixa do grupo, sem teste de hipótese humano × máquina |
| E1/E2/E3 | **Reavaliar os checkpoints aprovados**, sem retreino, com gravador passo a passo e randomização. Os números oficiais (59,000 / 60,050 / 52,525 s) continuam no texto |
| Imitação de humano | Fora do escopo (trabalho futuro) |
| Monografia | Título novo (comparativo direto); remover regulamentação (levar o *time trial* ao Estado da Arte); remover seção ROS2/contêiner; corte forte na Fundamentação |
| Git | Commit do estado atual como "versão hardware" e branch `escopo-comparativo` na monografia e no `f1tenth_code` |

## 1. O que já temos

**Código (`f1tenth_code/research/`)**
- `rollout.py`: `evaluate(policy_factory, track, n_seeds, n_laps, randomize)` mede qualquer `Policy` (`policy(obs, info) -> [esterço_norm, velocidade_norm]`), com IC de Wilson para conclusão e bootstrap para tempo de volta.
- `env.py`: física a 100 Hz, controle a 20 Hz (passo de 0,05 s), atraso de esterço de 100 ms, detector de colisão por segmento, randomização de atrito, largada e ruído.
- `info` traz por passo: `pose`, `v_x`, `d_lat`, `s`, `progress_m`, `sim_time`, `collision`, `scan_raw` (1080 feixes). Isso basta para todas as métricas novas.
- Runs aprovados: E1 `e1_pp_Spielberg_20260823-001606_…` (59,000 s; 50/50, **sem** randomização), E2 `e2_il_Spielberg_20260823-140231_…` (60,05 s; 50/50), E3 `e3_rl_Spielberg_20260823-211722_…` (52,52 s; 91/92).
- CLI: `python -m f1tenth_research eval --run-id <id> --track Spielberg --n-seeds 5 --n-laps 10` reavalia sem treinar.
- Pistas com mapa `.png/.yaml`, centerline e raceline em `research/assets/tracks/` (Spielberg e 4 held-out).
- Testes: 32 arquivos, `FakeF110` para testes rápidos, `test_spec_coverage.py` exige que todo ID novo do `SPEC.md` tenha teste.

**Não existe:** piloto humano, joystick dentro do `research/`, janela de visualização (pyglet e pygame ausentes), gravação
passo a passo, métricas de suavidade, desvio ou perfil de velocidade, seguidor de gap no `research/` (só como nó ROS2 em
`src/gap_follow/gap_follow/gap_follow.py`, 524 linhas, com PID e pontuação de gaps).

**Monografia:** 206 páginas. Cerca de 28% (~1.660 linhas) depende do carro ou da ponte sim-to-real. Já servem ao
comparativo: resultados de E1/E2/E3, critérios congelados, proveniência, Wilson, detector de colisão e o texto do *time
trial*. Falta todo o conteúdo sobre humanos (estado da arte, metodologia, resultados).

## 2. Objetivos finais da monografia

1. Implementar e avaliar em simulação controladores clássicos: o especialista *pure pursuit*, que também gera as demonstrações, e um seguidor de gap reativo;
2. Treinar uma política de imitação sem pose global e refiná-la por aprendizado por reforço residual, sob critérios fixados antes da medição;
3. Desenvolver uma interface de pilotagem humana no mesmo simulador e coletar voltas de pilotos humanos sob protocolo fixado antes da coleta;
4. Comparar os três tipos de piloto quanto a conclusão de volta, tempo de volta, colisões, suavidade do esterço, desvio da raceline e perfil de velocidade, com o humano em duas condições de informação (pista inteira e só LiDAR).

O bloco LaTeX da `PROPOSTA.md`, seção 1, precisa ser atualizado para estes quatro itens (entra o seguidor de gap no objetivo 1).

## 3. Fases

Cada fase lista entregáveis e o critério de pronto. As fases de código seguem o padrão do repositório: ID novo no
`SPEC.md`, teste que o cita, `pytest` verde, run registrado com proveniência.

### Fase 0 — Preparação (13–18/10/2026)
- [ ] Monografia: commit das 12 alterações pendentes como "versão hardware" e criar a branch `escopo-comparativo`.
- [ ] `f1tenth_code`: conferir o `git status`, commitar o que for do projeto e criar a branch `escopo-comparativo`.
- [ ] Adicionar `pygame` ao `research/pyproject.toml` (grupo opcional `human`), `uv lock` e instalar. Conferir que o joystick aparece no `pygame.joystick` e anotar índices de eixo e gatilho.
- **Pronto quando:** as duas branches existem, `pytest` continua verde e um script de 10 linhas imprime os eixos do joystick.

### Fase 1 — Medição passo a passo e métricas novas (19–31/10)
- [ ] `recorder.py`: um invólucro de `Policy` que grava por passo `sim_time`, ação, esterço aplicado, `v_x`, `d_lat`, `s`, `pose`, `collision`. Salva `steps.npz` no diretório do run. Não muda o comportamento da política.
- [ ] `metrics.py`, calculadas por volta concluída:
  - **suavidade do esterço:** média de |δₜ − δₜ₋₁| (rad por passo) e a mesma medida por segundo;
  - **desvio da raceline:** média e p95 de |d_lat|;
  - **perfil de velocidade:** `v_x` em função de `s`, reamostrado em bins fixos de distância (ex.: 1 m);
  - **curva de aprendizado:** tempo por volta em ordem cronológica (para humanos).
- [ ] Ligar o gravador ao `evaluate` por parâmetro opcional (padrão desligado, para não alterar runs antigos).
- [ ] IDs `SPEC-REC-*` e `SPEC-MET-*` com testes sobre `FakeF110` (ex.: esterço constante → suavidade 0; d_lat conhecido numa pista circular).
- **Pronto quando:** os testes passam e um E1 curto gera `steps.npz` e o relatório com as métricas.

### Fase 2 — Reavaliação de E1, E2 e E3 (01–08/11)
- [ ] Rodar a avaliação dos três checkpoints aprovados em Spielberg, **com randomização** e gravador, 5 seeds × 10 voltas.
- [ ] Atenção: o E1 oficial foi medido **sem** randomização. O E1 randomizado é um número **novo** para a comparação; o texto mantém os dois e diz qual é qual.
- [ ] Guardar o resultado como runs novos (`cmp_e1_…`, `cmp_e2_…`, `cmp_e3_…`) com o hash dos critérios.
- **Pronto quando:** existem três relatórios com conclusão, tempos e métricas novas, e os checkpoints usados batem com os runs aprovados.

### Fase 3 — Seguidor de gap no `research/` (01–15/11)
- [ ] Portar a lógica do nó ROS2 (pré-processamento do scan, detecção e pontuação de gaps, PID de esterço, velocidade em função do esterço) para uma `Policy` sem ROS, usando `info["scan_raw"]` e devolvendo ação normalizada pelos mesmos limites.
- [ ] Testes de unidade das funções puras (gaps num scan sintético).
- [ ] **Varredura curta de parâmetros** em Spielberg, no estilo do E1 (grade pequena de ganho, limiar de gap e velocidade máxima), com o critério de escolha escrito **antes** (ex.: maior conclusão, desempate pelo tempo).
- [ ] Congelar a configuração e avaliar com o protocolo da Fase 2 (randomização, gravador, 5 × 10).
- **Pronto quando:** existe um run `cmp_gap_…` com a configuração congelada e o registro da varredura. Desempenho ruim é resultado válido.

### Fase 4 — Interface de pilotagem humana (01–22/11)
- [ ] `human/joystick.py`: lê o analógico esquerdo (esterço, zona morta configurável) e o gatilho direito (velocidade 1–8 m/s), converte com `normalize_action`. Calibração dos eixos num arquivo de configuração por joystick.
- [ ] `human/policy.py`: `HumanPolicy` com a interface `Policy`. A cada chamada lê o joystick e **segura o passo até completar 0,05 s de relógio** (tempo real 1×). Se o passo de física atrasar, registra o atraso (para declarar).
- [ ] `human/render.py` (pygame):
  - **vista pista inteira:** mapa da pista (`<pista>_map.png`) visto de cima, carro na `pose` atual;
  - **vista só LiDAR:** pontos de `scan_raw` em coordenadas do carro, carro fixo no centro apontando para cima, sem mapa e sem rastro;
  - **HUD:** velocidade, tempo da volta atual e da última, sessão e volta.
- [ ] `human/session.py`: roteiro de uma sessão completa por piloto e vista:
  1. tela de identificação (código anônimo `P01`, `P02`…; nada de nome);
  2. treino de **10 min** cronometrados (episódios reiniciam após colisão; gravado em `treino/`, não conta);
  3. **3 sessões** cronometradas, cada uma um episódio com seed própria e alvo de 5 voltas; **colisão encerra a sessão**;
  4. pausa entre vistas; ordem fixa: pista inteira, depois só LiDAR.
- [ ] Saída por piloto: `runs/human_<Pxx>_<vista>_<data>/` com `config.yaml` (hash dos critérios, versão do código, joystick), relatório de volta igual ao `EvalReport` e `steps.npz` de cada sessão.
- [ ] Testes com joystick falso (sequência de eixos programada) e `FakeF110`: o ritmo de tempo real, a saturação dos limites, o fim da sessão em colisão e o formato da saída.
- **Pronto quando:** você completa uma sessão inteira nas duas vistas e o relatório sai no mesmo formato dos pilotos automáticos.

### Fase 5 — Protocolo e critérios congelados (23–29/11)
- [ ] `protocolo-humano.md` em `research/`: tudo que está na tabela de decisões (limites, vistas, treino, sessões, colisão, ordem, pista, randomização, métricas), mais o roteiro falado para o voluntário e o checklist da sala (mesma cadeira, monitor, joystick).
- [ ] Gravar o hash do protocolo no `config.yaml` de cada sessão (mesmo mecanismo do `gate_hash`).
- [ ] **Sessão-piloto** com você para validar o roteiro (não entra nos resultados), depois congelar.
- [ ] TCLE (termo de consentimento) e ficha curta do voluntário (experiência com jogos de corrida: nenhuma, alguma, bastante). Modelo pronto para o Comitê de Ética, se for necessário.
- **Pronto quando:** o protocolo está congelado e versionado e a sessão-piloto correu sem ajuste.

### Fase 6 — Coleta dos autores (30/11–13/12)
- [ ] Gustavo e Julio, cada um nas duas vistas, pelo protocolo congelado.
- [ ] Separar no texto: os autores conhecem o projeto, e você tem bastante experiência com jogos de corrida. Os dois aparecem como "autores", à parte dos voluntários.
- **Pronto quando:** existem 4 runs humanos (2 pilotos × 2 vistas) com relatório e métricas.

### Fase 7 — Apresentação ao orientador (meta: até 27/11/2026)
Você quer apresentar com o material já formatado. Esta fase **não pode passar de novembro**, porque a resposta sobre o
Comitê de Ética pode exigir submissão na Plataforma Brasil, que leva semanas.
- [ ] Pacote para o Filipe: `PROPOSTA.md` atualizada, este plano, os 4 objetivos, a tabela comparativa parcial (E1, E2, E3, gap e, se já houver, a sessão-piloto) e uma demonstração da interface.
- [ ] Perguntas fechadas para ele: (a) aceita a mudança de escopo e de título? (b) é preciso Comitê de Ética para voluntários? (c) aceita a ordem fixa das vistas e o estudo de caso descritivo? (d) algum avaliador já em vista?
- [ ] Combinar com o Julio que o TG III será pedido pelos dois em 2027.1, com carta de indicação nova.
- **Pronto quando:** as respostas (a) e (b) estão por escrito (e-mail).

### Fase 8 — Coleta dos voluntários (dez/2026 a fev/2027; **bloqueada pela Fase 7**)
- [ ] Se não precisar de CEP: 3 a 5 voluntários presenciais em dezembro e janeiro.
- [ ] Se precisar: submeter assim que o Filipe responder e coletar depois do parecer. Se o parecer não sair até meados de fevereiro, a monografia fecha só com os autores, e os voluntários viram trabalho futuro (declarado).
- [ ] TCLE assinado, código anônimo, dados guardados fora do git público.
- **Pronto quando:** cada voluntário tem os runs nas duas vistas e o TCLE arquivado.

### Fase 9 — Análise (jan–fev/2027)
- [ ] Tabela comparativa única em Spielberg com randomização: piloto (E1, gap, E2, E3, cada humano por vista), conclusão (Wilson), mediana e melhor volta, colisões, suavidade, desvio p95.
- [ ] Figuras: perfil de velocidade por piloto ao longo da volta; suavidade × tempo de volta; curva de aprendizado humano (treino + sessões); trajetórias sobrepostas numa curva difícil.
- [ ] Faixa do grupo humano (melhor, mediana, pior) e posição de cada política em relação a ela. Sem teste de hipótese.
- [ ] Script de análise versionado (`research/scripts/comparativo.py`) que regenera tabela e figuras dos runs.
- **Pronto quando:** tabela e figuras saem de um comando só, a partir dos runs registrados.

### Fase 10 — Monografia (remoções a partir de 16/11; texto novo jan–fev/2027)
Ordem pensada para a monografia continuar compilando a cada passo.

**10a. Remoções (16/11–20/12/2026)**
- [ ] Tirar `\include{capitulos/construcao_veiculo}` e `\include{capitulos/regulamentacao}` de `dissertacao.tex`. Antes, copiar o texto do *time trial* (`regulamentacao.tex:196-226`) para o Estado da Arte.
- [ ] `consideracoes.tex`: remover e mover o parágrafo que liga as Partes II e III (`:27-35`) para o fim do Estado da Arte, para a Parte I não ficar sem fechamento.
- [ ] `proposta.tex`: remover "Controle no veículo físico" (`:133-162`); ajustar abertura, organização do software (`:18-21`) e execução das políticas (`:166-181`).
- [ ] `metodologia_validacao.tex`: remover a ponte sim-to-real (`:918-1172`) e a Camada F/caso do contêiner (`:816-917`); reescrever "O escopo é a simulação" (`:1346`) como escolha e não como limitação; ajustar abertura (`:20-26`) e a tabela de camadas (`:706-712`, `:742-746`).
- [ ] `resultados.tex`: remover `sec:res-deploy` (`:566-692`) e `sec:res-s2r` com E4.1 (`:693-999`); ajustar abertura (`:12-19`) e Discussão (`:1171-1174`).
- [ ] `estadodaarte.tex`: reduzir `sec:arte-s2r` (`:622-700`) a um parágrafo que justifica a randomização (mantém Tobin e Peng); ajustar abertura (`:30-37`, `:47-48`) e o posicionamento (`tab:arte_posicionamento`, `:783-790`, `:842-844`).
- [ ] `ferramentas.tex` (corte forte): remover sensores e atuadores (`:114-158`), Nav2 (`:159-209`), tempo real embarcado (`:210-244`), mapeamento real (`:921-937`); reduzir odometria, base\_link e conceitos de navegação ao que o simulador usa; no sensoriamento, ficar só com LiDAR; no seguidor de parede, só a versão do simulador.
- [ ] `conclusao.tex`: remover "contrato de observação real" (`:262-320`) e "a sequência da transferência" (`:321-372`).
- [ ] Corrigir as referências órfãs: `sec:arte-s2r` (`estadodaarte:47`, `resultados:18`), `sec:res-s2r` (`conclusao:250`), `sec:res-e41` (`conclusao:258`), `sec:implementacao_pratica` (`ferramentas:809`) e todas as de `sec:res-deploy`/`tab:val_deploy` (`resultados:24, 616, 620, 1179`; `conclusao:49, 76, 405`; `metodologia:862, 1340, 1344`).
- [ ] Compilar com `latexmk` e conferir no `.log` que não há `undefined reference` nem `Citation … undefined`.
- **Pronto quando:** a monografia compila sem avisos de referência e não menciona mais o carro deste trabalho.

**10b. Texto novo (jan–fev/2027, depois das Fases 2–6)**
- [ ] `extras/dados.tex`: título novo (direção "comparativo direto", ex.: *Piloto humano, controle clássico e aprendizado de máquina na corrida autônoma F1TENTH: um estudo comparativo em simulação*), `\data{}`, "Título de Engenheiro(a)".
- [ ] Introdução: abertura, justificativa da comparação com humano, os 4 objetivos e a delimitação de escopo.
- [ ] Estado da arte: seção nova sobre pilotos humanos × controladores autônomos (ganchos já no texto: GT Sophy e Kaufmann em `:490`, clonagem de comportamento em `:325-329`) e o *time trial*.
- [ ] Proposta: seção do seguidor de gap e seção da interface humana (joystick, tempo real, duas vistas, HUD).
- [ ] Metodologia: protocolo humano, critérios congelados próprios, métricas novas, estudo de caso descritivo, ética (TCLE, anonimização, CEP se houver), assimetrias declaradas (ordem fixa, vista inteira × LiDAR, colisão encerra a sessão).
- [ ] Resultados: reavaliação com randomização (Fase 2), gap (Fase 3), humanos (Fases 6 e 8), tabela comparativa e figuras (Fase 9); Discussão com a `tab:res_sintese` atualizada.
- [ ] Conclusão: tabela dos 4 objetivos, trabalhos futuros curtos (hardware, imitação de humano, outras pistas), consideração final sem o carro.
- [ ] Resumo e abstract novos; palavras-chave sem "transferência simulação-realidade".
- [ ] Bibliografia: remover as entradas que ficarem sem citação (provável: `F1TENTHVESC`, `YDLIDARDriver`, `quigley2015programming`, `foote2013tf`, `casini2019response`, `Ghignone2025RLPP`, `Zhao2020Sim2Real`; conferir `thrun2005`) e acrescentar as da seção sobre humanos.
- **Pronto quando:** a monografia compila, a Conclusão responde aos 4 objetivos com números das Fases 2–9 e a revisão de ABNT foi feita.

### Fase 11 — TG III (2027.1)
- [ ] 01–05/02/2027: pedido de matrícula no TG III pelo formulário da DA-CECS, com carta de indicação nova, junto com o Julio.
- [ ] Indicar 3 a 5 avaliadores no prazo do calendário do quadrimestre (em 3Q2026 foi na 2ª semana).
- [ ] Monografia ao avaliador no prazo do quadrimestre (estimativa: ~6 semanas após o início, por volta de **meados de março de 2027**). Por isso o texto precisa estar fechado até **início de março**.
- [ ] Correções e versão final no Moodle com as fichas.

## 4. Cronograma resumido

| Período | Código e dados | Texto | Marcos |
|---|---|---|---|
| 13–18/10/2026 | Fase 0 | — | Branches criadas |
| 19/10–15/11 | Fases 1, 2, 3 | — | Métricas novas; E1/E2/E3/gap reavaliados |
| 01–22/11 | Fase 4 | Início 10a (16/11) | Interface humana pronta |
| 23–29/11 | Fase 5 | 10a | Protocolo congelado; **apresentação ao Filipe até 27/11** |
| 30/11–20/12 | Fase 6 | 10a concluída | Voltas dos autores; monografia sem o carro |
| dez/2026–fev/2027 | Fase 8 (depende do CEP) | — | Voluntários |
| jan–fev/2027 | Fase 9 | 10b | Tabela e figuras finais |
| 01–05/02/2027 | — | — | Pedido do TG III |
| até início de mar/2027 | — | 10b concluída | Monografia fechada |
| meados de mar/2027 (estimado) | — | — | Envio ao avaliador |

Em 2027.1 você também terá Mecânica dos Fluidos I e o estágio. Por isso o plano tenta fechar código e coleta até
dezembro, deixando para fevereiro só a análise e o texto.

## 5. Riscos e o que fazer

| Risco | Efeito | Resposta |
|---|---|---|
| CEP exigido e lento | Voluntários não entram a tempo | Apresentar ao Filipe até 27/11; se o parecer não sair até meados de fev, fechar só com os autores e declarar |
| Tempo real não se sustenta (passo > 50 ms) | Humano dirige em câmera lenta ou com engasgos | O gravador mede o atraso; se o p99 passar de 50 ms, reduzir o custo do render (vista sem mapa redesenhado a cada quadro) |
| Colisão encerra sessão → poucas voltas humanas | IC de Wilson muito largo | Declarado; o estudo é descritivo. As voltas de treino entram só na curva de aprendizado |
| Ordem fixa das vistas | O resultado só-LiDAR fica favorecido pelo aprendizado | Declarado como limitação; a curva de aprendizado mostra o tamanho do efeito |
| Gap follower ruim mesmo após a varredura | Clássico reativo sem voltas completas | É resultado: mostra o limite do reativo sem mapa, comparável à vista só-LiDAR |
| Monografia quebra ao remover seções | Atraso no fim | Remoções na ordem da Fase 10a, compilando a cada passo |
| Orientador não aceita a mudança | Plano volta para a versão só-simulação sem humano | A Fase 7 vem antes da coleta de voluntários e do texto novo, limitando a perda |

## 6. Limitações que o texto vai declarar

- Pilotos humanos com mais informação na vista de pista inteira do que as políticas (por isso a vista só-LiDAR).
- Ordem fixa das vistas.
- Amostra pequena (2 autores + 3 a 5 voluntários): estudo de caso, sem generalizar para "humanos".
- Autores separados dos voluntários: conhecem o projeto, e um deles tem bastante experiência com jogos de corrida.
- E1 oficial sem randomização × E1 do comparativo com randomização (os dois números aparecem).
- Uma pista só (Spielberg).
