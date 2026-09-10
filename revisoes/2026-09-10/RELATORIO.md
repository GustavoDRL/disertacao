# Revisão técnica do projeto TG — 10/09/2026

Foram identificados **27 achados: 7 de prioridade alta (P1), 18 de prioridade média (P2) e 2 de prioridade baixa (P3)**. Os problemas mais relevantes estão na cadeia de emergência do carro, na consistência entre observação simulada e execução real e nos mecanismos que aprovam experimentos. **1.111 testes passaram**, mas as reproduções adicionais demonstram que esse resultado não cobre todos os contratos de integração.

Esta revisão não alterou código de produção, configuração, modelos ou resultados científicos. Os arquivos desta pasta são o relatório e suas evidências. Não foi realizado teste com atuadores físicos, nem inferida aprovação para circulação do carro.

## Escopo e método

| Área | Estado examinado | Trabalho realizado |
|---|---|---|
| `f1tenth_code` | commit `fabf7e5`, 551 arquivos versionados | Pesquisa, treino/avaliação, gates, MCP, telemetria, simulador, pacotes ROS, Docker e documentação operacional |
| `f1tenth_code/car` | parte do repositório acima | Guarda, adaptador LiDAR, política embarcada, wall following, servo, conversores VESC, launch, scripts e testes |
| `f1tenth_code_rasp` | commit `a43ec67`, 172 arquivos versionados | Comparação de estrutura, documentação de instalação e coexistência com a cópia ativa do carro |
| `f1tenth_gym_ufabc` | commit `e054fdf`, 65 arquivos versionados | Identificação do fork arquivado e comparação com a ponte ativa |
| `disertacao` | commit `2a7537b`, 27 arquivos versionados | Compilação completa e cruzamento de descrições técnicas com a implementação e o estado dos experimentos |
| `f1tenth_notes` | commit `6612b4a`, 49 arquivos versionados | Inventário e identificação como material de notas/referência |

A revisão combinou leitura dos caminhos de execução, comparação entre componentes, análise sintática, execução das suítes disponíveis e sondas específicas dos casos de borda. O foco da análise aprofundada foi a implementação ativa. O conteúdo de notas, histórico, dependências externas e todos os dados brutos de treino não receberam leitura integral linha a linha. Não houve auditoria bibliográfica externa nem verificação jurídica/normativa das regras da competição.

No início não havia índice CodeGraph nos repositórios principais inspecionados. Um `.codegraph/` não versionado apareceu em `f1tenth_code_rasp` durante a revisão; não foi criado ou alterado pelas ações desta revisão. As alterações preexistentes do fork `f1tenth_gym_ufabc` foram preservadas.

## Verificações executadas

| Verificação | Resultado |
|---|---|
| `f1tenth_code`: `./research/.venv/bin/python -m pytest tests -q` | **143 passed** |
| `research`: `.venv/bin/python -m pytest` | **421 passed**, 11 deselected |
| `research`: `.venv/bin/python -m pytest -m sim` | **11 passed**, 421 deselected |
| `car`: `../research/.venv/bin/python -m pytest tests -q -m 'not hardware and not performance and not slow'` | **536 passed**, 2 skipped, 24 deselected |
| Camadas C/D/E do verificador, chamadas diretamente | C: **6/6**; D: PASS com **25 avisos declarados**; E: PASS |
| Análise sintática dos arquivos versionados, excluindo build/install e dependências vendorizadas | **227 Python**, **31 shell**, **26 package.xml**, sem erro sintático |
| `latexmk -pdf -interaction=nonstopmode -halt-on-error` em diretório temporário | **206 páginas**, compilação concluída; persistem avisos de composição |
| Sondas adicionais deste relatório | Executadas com sucesso, confirmando os comportamentos defeituosos descritos |

O Docker estava acessível, mas `docker compose ps` não mostrou serviços ativos. Não foram executados build limpo da imagem, launch ROS real, Camada F/deploy ou testes de hardware. C1/C podem conferir evidências em disco: seu PASS nesta sessão não significa que foi feita uma nova execução no container. Testes com dublês verificam lógica Python, mas não comprovam QoS, escalonamento do executor ou resposta elétrica do VESC.

Reprodução das sondas, a partir de `TG/`:

```bash
f1tenth_code/research/.venv/bin/python revisao-2026-09-10/reproduzir.py
```

As asserções desse script confirmam o comportamento atual defeituoso. Não são testes de aceitação das futuras correções. Saída integral em [reproducoes.txt](reproducoes.txt); código em [reproduzir.py](reproduzir.py).

## Achados de prioridade alta

### R01 — A emergência do servo não bloqueia os comandos concorrentes de velocidade ao VESC

**P1 — segurança de atuação.** Quando o pigpio falha e `/drive` continua chegando, o servo publica zero no comando de motor a 10 Hz. Em paralelo, `ackermann_to_vesc` continua convertendo cada `/drive` em um comando de velocidade. O driver aceita os dois callbacks independentemente; não há estado comum que iniba `setSpeed` durante a emergência. Portanto, publicar zero repetidamente não garante que os comandos seguintes de aceleração sejam recusados.

Evidência: [ramo de emergência](/home/disney/Documents/repos/TG/f1tenth_code/car/src/f1tenth_control/f1tenth_control/servo_control_node.py:553), [publicação de zero](/home/disney/Documents/repos/TG/f1tenth_code/car/src/f1tenth_control/f1tenth_control/servo_control_node.py:669), [conversor independente](/home/disney/Documents/repos/TG/f1tenth_code/car/src/vesc-humble/vesc_ackermann/src/ackermann_to_vesc.cpp:71), [callbacks do driver](/home/disney/Documents/repos/TG/f1tenth_code/car/src/vesc-humble/vesc_driver/src/vesc_driver.cpp:271). Fluxo confirmado por inspeção; a resposta física não foi medida.

**Correção sugerida:** estabelecer uma autoridade única para a saída do motor, com emergência persistente que iniba comandos não nulos até recuperação explícita. Testar o fluxo integrado com `/drive` contínuo e falha do servo; conferir apenas que `_stop_motor()` publicou zero é insuficiente.

### R02 — O `wall_follow` ignora a calibração angular e o espelhamento do adaptador

**P1 — geometria de controle.** O launch autônomo sobe `scan_adapter_node`, mas o `wall_follow` continua assinando `/scan` pelo seu YAML. `profile_path`, `angle_offset_rad` e `espelhar` só afetam `/scan_sim`. A recomendação de calibrar o zero angular antes dos estágios no chão não faz essa correção chegar ao controlador que está autorizado nesses estágios. Uma montagem que exija espelhamento pode fazer o controlador medir a parede do lado errado.

Evidência: [launch do controlador](/home/disney/Documents/repos/TG/f1tenth_code/car/src/sim2real_bridge/launch/autonomo.launch.py:171), [tópico bruto configurado](/home/disney/Documents/repos/TG/f1tenth_code/car/src/wall_follow/config/wall_follow.yaml:11), [leitura dos ângulos sem perfil](/home/disney/Documents/repos/TG/f1tenth_code/car/src/wall_follow/wall_follow/wall_follow.py:106).

**Correção sugerida:** compartilhar a transformação geométrica com o controlador ou fornecer-lhe um scan corrigido, preservando a identificação de pontos inválidos. Testar a cadeia completa com offset e espelhamento não triviais; trocar simplesmente o tópico exige conferir também os valores de preenchimento.

### R03 — A política dirige sem nunca receber odometria e continua com odometria vencida

**P1 — validade da observação.** `_v_x` nasce em zero. `_control_step()` exige apenas scan e não verifica se houve odometria, sua idade ou finitude. Com LiDAR ativo e VESC/odom ausente, a rede continua produzindo comandos frescos e a guarda não entra em timeout. A velocidade é parte explícita da entrada do modelo.

Evidência: [callback de odometria e controle](/home/disney/Documents/repos/TG/f1tenth_code/src/policy_runner/policy_runner/policy_node.py:154). A sonda `POLITICA_SEM_ODOM` executou o nó real com sessão ONNX dublada e publicou **6 m/s sem nenhuma mensagem de odometria**.

**Correção sugerida:** exigir primeira odometria válida, adicionar timeout monotônico, recusar não finitos e publicar parada quando esse contrato falhar. O comentário do script de gate afirmando que a inferência exige scan e odom também precisa ser corrigido.

### R04 — O estado recorrente do E3 descreve o comando anterior à guarda como se tivesse sido aplicado

**P1 — paridade simulação/execução.** No carro, a política publica `/drive_raw`, e a guarda pode limitar velocidade, cortar por deadman ou alterar esterço. Entretanto, `fecha_passo()` registra a ação produzida pela política como `speed_aplicada`/`steer_aplicado`. O nó não recebe a decisão final da guarda. Exemplo: rede pede 6 m/s, guarda limita a 1 m/s ou impede movimento, mas `proprio_env` do próximo passo descreve 6 m/s. Na avaliação com `com_cap`, a ação limitada chega ao ambiente e a observação seguinte contém esse limite.

Evidência: [realimentação local](/home/disney/Documents/repos/TG/f1tenth_code/src/policy_runner/policy_runner/policy_node.py:258), [remap para comando bruto](/home/disney/Documents/repos/TG/f1tenth_code/car/src/sim2real_bridge/launch/autonomo.launch.py:146), [cap na simulação](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/sim2real.py:317). A sonda confirma o valor 6 no estado local; a divergência após a guarda decorre da topologia.

**Correção sugerida:** realimentar o comando final autorizado no estado do ambiente, mantendo separado o estado próprio da rede base. Incluir limites, deadman e retomada no teste de paridade temporal.

### R05 — Os gates E2/E3 aprovam relatórios sem critérios obrigatórios

**P1 — validade dos resultados.** Os critérios de held-out só são adicionados quando `heldout` é verdadeiro; os critérios de atrito só aparecem quando `mu_paired` é verdadeiro. Se as medições faltarem, o gate pode devolver PASS apenas com completion e tempo de volta. Também não exige o conjunto completo de pistas quando um held-out parcial é fornecido.

Evidência: [condicional do E2](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/gate.py:315), [condicional do E3](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/gate.py:330). Ambas as sondas `GATE_SEM_MEDICOES` retornaram **PASS com dois critérios**.

**Correção sugerida:** validar esquema, campos e conjunto esperado de medições antes de pontuar. Ausência de evidência obrigatória deve gerar resultado inválido/indeterminado ou reprovação explícita. Este achado não demonstra que os runs históricos citados estejam incompletos; demonstra que o gate não impede a aprovação de um relatório incompleto.

### R06 — Colisão no passo que cruza a chegada pode contar como volta limpa

**P1 — contagem científica.** `rollout_episode()` registra completion antes de examinar `terminated` e `info['collision']`, preenchendo `collision=False` na volta concluída. Se a meta de voltas é atingida, o `break` elimina por completo o registro da colisão. Nas demais voltas, pode registrar uma volta limpa e atribuir a colisão à tentativa seguinte.

Evidência: [ordem dos testes](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/rollout.py:110). Uma sonda com `progress_m=10.1`, pista de 10 m e `collision=True` devolveu somente uma volta **completed=True, collision=False**.

**Correção sugerida:** estabelecer precedência explícita para colisão no mesmo passo de física/controle e registrar o evento sem perder sua atribuição. Verificar os registros históricos para identificar se algum episódio atingiu esse caso antes de recalcular números citados.

### R07 — O gate de 60 segundos pode aprovar uma janela que parou de atualizar

**P1 — falso aceite de runtime.** Ao final, `medir_gate_s2r.sh` compara o mtime do arquivo apenas com o início da execução. Um arquivo atualizado por 20 s e congelado pelo restante da janela ainda passa nessa condição. A taxa é calculada pelo delta de `uptime_sec` do próprio arquivo; não há exigência de que ele corresponda aos 60 s reais. Um processo vivo, mas travado após produzir dados bons, pode satisfazer o julgamento.

Evidência: [checagem de mtime](/home/disney/Documents/repos/TG/f1tenth_code/car/scripts/test/medir_gate_s2r.sh:205), [denominador da taxa](/home/disney/Documents/repos/TG/f1tenth_code/car/scripts/test/medir_gate_s2r.sh:239). O julgador Python original aprovou **400 inferências em somente 20 s**, embora o contrato seja sustentação por 60 s.

**Correção sugerida:** amostrar saúde durante toda a janela, exigir avanço contínuo, limitar idade da última amostra e comparar duração observada com relógio monotônico externo. Ler cada snapshot uma única vez, evitando combinar campos de versões diferentes do JSON.

## Achados de prioridade média

### R08 — O gate mede inferência recente, não p99 do ciclo durante toda a janela

O SPEC-S2R-21 exige p99 do ciclo e CPU sustentados por 60 s. `latency_ms` encerra a medição antes de saturação, publicação e atualização do estado; guarda apenas 500 amostras, equivalentes a aproximadamente 25 s a 20 Hz. O script usa apenas o p99 final. Picos no começo da janela podem desaparecer. `%cpu` de `ps` é média desde o início do processo, não uso durante cada intervalo; pode diluir sobrecarga posterior, ao contrário do comentário que afirma que só erra para reprovar.

Evidência: [buffer de latências](/home/disney/Documents/repos/TG/f1tenth_code/src/policy_runner/policy_runner/policy_node.py:126), [fim da medição](/home/disney/Documents/repos/TG/f1tenth_code/src/policy_runner/policy_runner/policy_node.py:237), [CPU](/home/disney/Documents/repos/TG/f1tenth_code/car/scripts/test/medir_gate_s2r.sh:199), [contrato](/home/disney/Documents/repos/TG/f1tenth_code/research/SPEC.md:801). **Correção:** instrumentar o ciclo completo e agregar latências e deltas de CPU sobre a janela efetivamente julgada.

### R09 — A reavaliação genérica oferecida pelo MCP não carrega políticas E3

`evaluate_policy()` aceita runs E3 e chama o subcomando `eval`, mas `reevaluate()` trata todo run não E1 como uma `TinyLidarNet` em `best.pt`. O E3 aprovado tem **`sac.zip` e `policy.onnx`**, sem `best.pt`. A chamada falha ao carregar o arquivo, antes de avaliar. Para E1, o mesmo caminho lê o baseline global atual em vez da configuração do run solicitado, podendo avaliar outro expert sob o identificador antigo.

Evidência: [carregamento genérico](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/stages.py:1021), [tool MCP](/home/disney/Documents/repos/TG/f1tenth_code/mcp_server/research_tools.py:255). **Correção:** selecionar o carregador pela etapa/configuração congelada, reutilizando a fábrica E3 existente e o PPConfig do E1 solicitado; tornar o resultado assíncrono rastreável no status.

### R10 — O MCP procura um campo `stage` que os arquivos de status não contêm

`run_experiment()` usa `status['stage']` para impedir treino concorrente e descobrir o run recém-criado. `Run.set_status()` não grava esse campo, e `_all_status()` não o acrescenta. **Todos os 22 runs reais examinados estavam sem `stage` em `status.json`.** Assim, o bloqueio por etapa não reconhece runs ativos e a busca do identificador não encontra o run novo pelo critério usado. Há ainda uma corrida porque o conjunto `antes` é capturado depois de `Popen`.

Evidência: [filtros](/home/disney/Documents/repos/TG/f1tenth_code/mcp_server/research_tools.py:149), [status efetivamente escrito](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/runs.py:171). **Correção:** derivar etapa do config/identificador ou gravá-la consistentemente; capturar o inventário antes do lançamento. Cobrir a integração com `Run.create`, não apenas fixtures que inventam o campo.

### R11 — O `verify` não executa os testes do carro

`layer_b_tests()` roda pesquisa e a pasta `tests/` da raiz; `--full` acrescenta somente testes `sim`. A suíte de `car/tests` fica fora do verificador central, embora ali estejam as verificações de guarda, servo, joystick, scripts e launch.

Evidência: [Camada B](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/verify.py:85). Foram **536 testes adicionais aprovados** quando essa suíte foi executada separadamente. **Correção:** incorporá-la como subprocesso independente e manter as exclusões explícitas de hardware/performance, sem misturar os conftests das três suítes.

### R12 — A checagem de proveniência já deixa o E1 citado fora da inspeção

`layer_e_provenance()` usa `list_runs()` com o limite padrão de 20 e só depois procura os aprovados por etapa. Existem 22 runs; o E1 que sustenta o baseline está entre os dois que ficam de fora. A camada retorna PASS sem verificar o `gate_hash` desse E1.

Evidência: [consulta limitada](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/verify.py:158), [limite padrão](/home/disney/Documents/repos/TG/f1tenth_code/research/f1tenth_research/runs.py:258), [inventário reproduzido](proveniencia.json). **Correção:** resolver diretamente os runs efetivamente referenciados por baseline, política base e modelo em uso; não depender de paginação cronológica global.

### R13 — A guarda aceita configurações que contradizem o próprio envelope

`Limites` não valida domínio, finitude ou sinal. Com `max_speed_mps=-1`, o clamp devolve **-1 m/s com motivo `ok`**, mesmo com comando positivo e com a regra declarada de proibir ré. Timeouts `NaN` também podem fazer comparações de expiração nunca serem verdadeiras.

Evidência: [clamp](/home/disney/Documents/repos/TG/f1tenth_code/car/src/sim2real_bridge/sim2real_bridge/guarda.py:116); sonda `LIMITE_NEGATIVO`. O problema exige parâmetro/configuração inválido, não acontece com o YAML padrão. **Correção:** validar valores finitos e faixas na construção, inclusive botões, prazos e relação entre limites, antes de criar publishers.

### R14 — O adaptador aceita um scan com um único feixe e o transforma em espaço livre

A fração válida usa como denominador os pontos recebidos na janela, sem validar cobertura angular ou densidade. Um scan com um feixe válido em 0 rad tem fração 100%; a lógica de lacunas preenche a saída inteira. A sonda produziu **1.080 feixes a 12 m** a partir de **um obstáculo a 1 m**, em vez de descartar a entrada.

Evidência: [validação de fração](/home/disney/Documents/repos/TG/f1tenth_code/car/src/sim2real_bridge/sim2real_bridge/adaptador.py:144), [preenchimento](/home/disney/Documents/repos/TG/f1tenth_code/car/src/sim2real_bridge/sim2real_bridge/adaptador.py:184). **Correção:** exigir cobertura/densidade mínima compatível com o perfil e medir a proporção realmente observada na saída; tratar scan truncado como falha de observação.

### R15 — A política não contém saídas não finitas e quebra com scan vazio

`np.clip` preserva NaN. Uma inferência que retorne NaN publica NaN e contamina o estado recorrente. O tratamento de exceções não cobre esse caso, pois nenhuma exceção é lançada. Um scan vazio, por sua vez, gera índices para um array vazio e provoca `IndexError` fora da proteção de inferência.

Evidência: [recepção de scan](/home/disney/Documents/repos/TG/f1tenth_code/src/policy_runner/policy_runner/policy_node.py:140), [pós-processamento da ação](/home/disney/Documents/repos/TG/f1tenth_code/src/policy_runner/policy_runner/policy_node.py:246); ambas as sondas reproduzidas. A guarda do carro contém comandos NaN, mas o simulador recebe a publicação direta e o estado interno permanece corrompido. **Correção:** validar formato/finitude de entradas e saídas e definir recuperação segura do estado.

### R16 — A telemetria dá timestamp novo a medições antigas

O coletor reescreve a última odometria e o último scan com `timestamp=now` a cada snapshot, mesmo que a fonte tenha parado. O MCP usa o timestamp do JSON para avisar sobre dados antigos; por isso, um coletor vivo pode apresentar sensores mortos como estado atual. A trajetória também recebe cópias da pose antiga com tempos novos.

Evidência: [timestamp de scan](/home/disney/Documents/repos/TG/f1tenth_code/src/data_collector/data_collector/collector_node.py:116), [timestamp de estado](/home/disney/Documents/repos/TG/f1tenth_code/src/data_collector/data_collector/collector_node.py:154), [aviso do MCP](/home/disney/Documents/repos/TG/f1tenth_code/mcp_server/server.py:50). **Correção:** separar instante de gravação e idade de cada fonte; não sintetizar observações novas ou métricas de movimento a partir de entradas vencidas.

### R17 — O detector de `stuck` acusa travamento durante movimento lento contínuo

O detector compara a posição com a amostra imediatamente anterior, mas exige deslocamento acima de 5 cm para atualizar `last_move_time`. A 10 Hz, velocidades abaixo de aproximadamente 0,5 m/s deslocam menos que isso em cada amostra. A referência é substituída a cada chamada e o deslocamento acumulado nunca conta. Na sonda, o carro a 0,4 m/s já tinha percorrido **1,24 m** quando recebeu evento `stuck`.

Evidência: [comparação de deslocamento](/home/disney/Documents/repos/TG/f1tenth_code/src/data_collector/data_collector/failure_detector.py:105), [atualização da referência](/home/disney/Documents/repos/TG/f1tenth_code/src/data_collector/data_collector/failure_detector.py:71). **Correção:** medir progresso acumulado em janela temporal ou manter uma referência até ultrapassar a distância mínima. O erro afeta a nota de algoritmos, especialmente os lentos.

### R18 — O YAML padrão do launch `gap_follow` não tem estrutura de parâmetros ROS2

O arquivo contém escalares na raiz (`max_range`, `max_speed` etc.), mas é passado como caminho em `Node(parameters=[params_file, ...])`. Falta o bloco do nó ou `/**` com `ros__parameters`. É um YAML sintaticamente válido e, por isso, passa em um parser genérico; não é um arquivo de parâmetros ROS2 válido para esse consumo.

Evidência: [arquivo](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/config/gap_follow.yaml:1), [consumidor](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/launch/gap_follow.launch.py:32). Confirmação estática do contrato; não foi executado launch ROS nesta máquina. **Correção:** ajustar a estrutura e incluir um teste de inicialização real do launch.

### R19 — O launch do gap usa tempo simulado, mas a ponte não publica `/clock`

O default `use_sim_time=true` faz os timers do nó dependerem do relógio de simulação. A ponte ativa cria timers de parede e publica scan/odom/TF, mas não publica `/clock`; o compose também não inicia outro provedor. Assim, mesmo corrigindo o YAML, o launch padrão pode ficar com os timers de processamento e controle sem avançar. Executar o nó diretamente pelo MCP evita esse default, o que explica comportamentos diferentes entre as duas formas de iniciar.

Evidência: [default do launch](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/launch/gap_follow.launch.py:14), [timers da ponte](/home/disney/Documents/repos/TG/f1tenth_code/src/f1tenth_gym_ros/f1tenth_gym_ros/gym_bridge.py:129). **Correção:** escolher um contrato único de relógio; publicar `/clock` coerente com a física ou usar tempo de parede em todos os consumidores desse setup.

### R20 — O gap assina `/odom`, mas o simulador publica `/ego_racecar/odom`

O controle de velocidade do gap depende de `current_speed`, atualizado pelo subscriber relativo `odom`. Não há remap no launch para o tópico da ponte ativa. No namespace padrão, o callback não recebe a odometria esperada e a malha de velocidade opera com o valor inicial zero.

Evidência: [subscriber](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/gap_follow/gap_follow.py:270), [configuração do simulador](/home/disney/Documents/repos/TG/f1tenth_code/src/f1tenth_gym_ros/config/sim.yaml:1). **Correção:** parametrizar/remapear o tópico e exigir odometria válida antes de operar a malha fechada.

### R21 — O gap continua dirigindo sobre o último scan indefinidamente

O callback armazena o scan, e o timer o reprocessa sem verificar idade; o controle também não utiliza a idade de `ScanData`. Se a fonte parar, comandos novos continuam saindo sobre geometria antiga. A sonda executou `_on_control_timer` com timestamp muito antigo e recebeu comando de **0,5 m/s**.

Evidência: [processamento periódico](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/gap_follow/gap_follow.py:288), [controle sem frescor](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/gap_follow/gap_follow.py:393). O pacote é usado no simulador; não atribuir esse achado ao wall following novo do carro. **Correção:** timeout por recepção/idade do sensor e parada explícita para dados vencidos.

### R22 — A ponte publica incremento angular incompatível com os próprios feixes

A ponte usa `scan_fov / scan_beams`; o simulador e o adaptador usam `fov / (n-1)` para os extremos inclusivos. Com 1.080 feixes e FOV de 4,7 rad, o último ângulo calculado pelos metadados fica **0,00435185 rad (0,24934°)** aquém de `angle_max`. Consumidores que usam incremento e consumidores que usam `linspace(angle_min, angle_max, n)` interpretam geometrias diferentes para o mesmo scan.

Evidência: [incremento da ponte](/home/disney/Documents/repos/TG/f1tenth_code/src/f1tenth_gym_ros/f1tenth_gym_ros/gym_bridge.py:97), [geometria do adaptador](/home/disney/Documents/repos/TG/f1tenth_code/car/src/sim2real_bridge/sim2real_bridge/adaptador.py:27). **Correção:** gerar metadados a partir da mesma geometria do simulador e testar a identidade entre último índice e `angle_max`.

### R23 — O caminho de instalação inicial não compila nem inicia o workspace ROS

O README apresenta `docker compose up --build` como inicialização e depois orienta a dar source em `/sim_ws/install/setup.bash`. O Dockerfile instala dependências, mas não executa `colcon build`; o entrypoint é apenas `/bin/bash`. O compose monta o clone sobre `/sim_ws` e não fornece comando de build/launch. Em clone novo, o `install/setup.bash` esperado não é produzido por esse procedimento e o simulador não é lançado automaticamente.

Evidência: [instruções iniciais](/home/disney/Documents/repos/TG/f1tenth_code/README.md:39), [etapa chamada de build](/home/disney/Documents/repos/TG/f1tenth_code/Dockerfile:87), [entrypoint](/home/disney/Documents/repos/TG/f1tenth_code/Dockerfile:113), [compose](/home/disney/Documents/repos/TG/f1tenth_code/docker-compose.yml:1). **Correção:** documentar e validar bootstrap completo de clone limpo, incluindo build, source e launch. O build de imagem não foi executado nesta revisão; este achado trata dos passos ausentes no fluxo versionado.

### R24 — A dissertação descreve algoritmos e arquitetura diferentes do código ativo

O capítulo de proposta descreve `WallFollow` com PID, mas `f1tenth_code/src/wall_follow` implementa `WallFollowHybrid`, um **Disparity Extender**. A versão PID por geometria está em `car/src/wall_follow` e tem outra implementação. O capítulo também descreve threads dedicadas e filas para o gap; o código atual usa timers, atributos `latest_scan*` e `rclpy.spin(node)` sem executor multithread explícito. Há nomes de pacotes apresentados como implementados que não correspondem aos reais: `joy_control`, `mapping` e `visualization` versus `joy_converter`, `my_robot_mapper` e `perfil_lidar`.

Evidência: [descrição de pacotes](/home/disney/Documents/repos/TG/disertacao/capitulos/proposta.tex:33), [PID de parede](/home/disney/Documents/repos/TG/disertacao/capitulos/proposta.tex:129), [arquitetura de threads/filas](/home/disney/Documents/repos/TG/disertacao/capitulos/proposta.tex:840), [algoritmo ativo](/home/disney/Documents/repos/TG/f1tenth_code/src/wall_follow/wall_follow/wall_follow.py:3), [executor do gap](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/gap_follow/gap_follow.py:504).

**Correção:** identificar explicitamente versões históricas e commits quando forem objeto do texto; caso o capítulo pretenda descrever o sistema atual, atualizar equações, classes, diagramas e nomes. A ressalva existente de que os algoritmos não foram validados no carro é correta, mas não resolve a divergência de implementação.

### R25 — O repositório antigo do Raspberry ainda se apresenta como caminho operacional

`f1tenth_code_rasp/README.md` continua instruindo clone/update e execução de `scripts/build_and_test_f1tenth.sh` e `f1tenth_control.launch.py`, ausentes nessa árvore. Também recomenda um nome de launch de joystick com `.launch.py` enquanto a cópia antiga guarda `launch_joy_ackerman_fixed.py`. O código de carro ativo e revisado está em `f1tenth_code/car`. Ao contrário do fork do simulador, o README antigo do Raspberry não abre com aviso claro de arquivamento/migração.

Evidência: [instruções legadas](/home/disney/Documents/repos/TG/f1tenth_code_rasp/README.md:55), [caminho atual](/home/disney/Documents/repos/TG/f1tenth_code/car/README.md:1). **Correção:** colocar aviso de migração no topo, apontar a fonte ativa e retirar passos que parecem instaláveis. Manter o histórico identificado reduz a chance de aplicar correções na cópia errada ou instalar controles antigos.

## Achados de prioridade baixa

### R26 — O PDF final ainda inclui conteúdo de template e instruções editoriais

A compilação inclui “Figura X (inserir diagrama...)”, “Palavra-chave1/2”, “Universidade xxx”, “Faculdade de xxx”, aprovação datada de **01 de janeiro de 2014**, assinaturas genéricas e listas de símbolos/siglas herdadas do modelo. Isso não é erro de compilação: entra no documento entregue. Também permanecem caixas de texto excedendo margens, registradas no log final.

Evidência: [Figura X](/home/disney/Documents/repos/TG/disertacao/capitulos/proposta.tex:28), [ficha](/home/disney/Documents/repos/TG/disertacao/pretextual/catalografica.tex:35), [aprovação](/home/disney/Documents/repos/TG/disertacao/pretextual/assinaturas.tex:35), [listas](/home/disney/Documents/repos/TG/disertacao/dissertacao.tex:161), [log da compilação](latex-final.log). **Correção:** substituir ou omitir blocos ainda não preenchidos conforme a versão do trabalho, revisar as listas e inspecionar visualmente os trechos com `Overfull` antes da entrega.

### R27 — O pacote gap instala um comando apontando para módulo inexistente

`setup.py` declara `pid_visualizer = gap_follow.pid_visualizer:main`, mas `gap_follow/pid_visualizer.py` não existe na árvore versionada. O entrypoint pode ser gerado durante instalação e só falhar quando executado.

Evidência: [entrypoint](/home/disney/Documents/repos/TG/f1tenth_code/src/gap_follow/setup.py:28). **Correção:** remover o comando obsoleto ou restaurar uma implementação testada; validar os alvos dos entrypoints contra os módulos empacotados.

## Ordem sugerida para correção e critérios de fechamento

1. **R01–R04:** corrigir a autoridade de emergência e o contrato de observação/ação. Fechar com teste integrado de falha do servo enquanto comandos continuam chegando, perda de odometria, calibração não nula e aplicação de limites/deadman.
2. **R05–R08:** tornar o aceite científico e o aceite de runtime resistentes a ausência de dados, colisão na chegada, congelamento e métricas medidas fora da janela. Só recalcular resultados históricos quando houver evidência de que o caso afetou um run; preservar os artefatos originais.
3. **R09–R17:** alinhar MCP, status, proveniência, verificação central, entradas inválidas e telemetria. Fechar com testes de integração entre produtores e consumidores reais dos arquivos/status, sem fixtures que acrescentem campos inexistentes.
4. **R18–R23 e R27:** validar pacote/launch e bootstrap em ROS2 real a partir de clone limpo. Separar esse teste de instalação da suíte sem ROS.
5. **R24–R26:** ajustar texto e fontes de documentação depois de decidir quais versões representam o sistema entregue.

Os resultados positivos das suítes e da compilação são evidência útil. Eles não anulam os achados, porque várias inconsistências estão justamente entre componentes testados isoladamente ou entre o que é medido e o que o veredito afirma.
