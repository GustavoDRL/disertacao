# Correções da revisão de 10/09/2026

Os 27 achados do [relatório original](RELATORIO.md) foram tratados no código e na documentação. As alterações estão no workspace, sem commit. O relatório e as sondas originais descrevem o estado anterior; `reproduzir.py` contém propositalmente as asserções dos defeitos antigos e não é a suíte de regressão das correções.

| Achado | Correção realizada |
|---|---|
| R01 | Interdição no driver VESC, habilitação com prazo de validade e rearme por comando neutro após a direção responder. |
| R02 | Wall following físico aplica espelhamento e deslocamento angular do perfil de montagem. |
| R03 | Política exige odometria recente e finita; ausência ou expiração produz parada. |
| R04 | Guarda confirma o comando autorizado; política usa essa confirmação na memória do ambiente e mantém a memória base separada. Sem confirmação, publica parada. |
| R05 | E2 exige as pistas held-out declaradas; E3 exige ambas as medidas de atrito pareadas. Evidência ausente reprova. |
| R06 | Colisão tem precedência sobre cruzamento da chegada na contagem de voltas. |
| R07 | Gate acompanha continuamente a saúde e verifica duração externa, frescor, reinício e amostras faltantes. |
| R08 | Instrumentação do ciclo inteiro, agregação de todos os ciclos da janela e CPU por deltas do processo. |
| R09 | Reavaliação usa PPConfig congelado do E1, rede do E2 ou fábrica SAC do E3. Status auxiliar por pista registra execução, conclusão e erro, exposto pelo MCP sem alterar o veredito do treino. |
| R10 | Status novo grava etapa; MCP deriva etapa de identificadores antigos e captura o inventário antes de iniciar o processo. |
| R11 | `verify` inclui a suíte do carro, com exclusões explícitas de hardware, desempenho e testes lentos. |
| R12 | Proveniência consulta todos os runs e resolve referências do baseline, do modelo `best` e de suas políticas base. |
| R13 | Guarda valida finitude, sinal e limites de configuração antes de publicar. |
| R14 | Adaptador rejeita um único feixe e cobertura angular insuficiente. A fração mínima configurada também considera os feixes de saída efetivamente cobertos. |
| R15 | Política rejeita scan vazio e ações não finitas ou de formato inválido, sem contaminar a memória. |
| R16 | Telemetria preserva instante de aquisição, separa instante de escrita e evita repetir pontos de trajetória sem nova odometria. |
| R17 | Detector acumula deslocamento em relação à referência de movimento, evitando falso travamento em movimento lento. |
| R18 | YAML do gap usa a estrutura ROS2 correta. Callback de parâmetros é registrado após inicialização. |
| R19 | Launch usa relógio do sistema, coerente com a ausência de `/clock`. |
| R20 | Tópico padrão de odometria do gap corresponde ao simulador. |
| R21 | Gap invalida dados e publica parada quando scan ou odometria expiram. |
| R22 | Incremento angular da ponte usa abertura dividida por N−1. |
| R23 | Compose chama script que compila o workspace, carrega o overlay e inicia o launch. README contém URL real e procedimento coerente. |
| R24 | Capítulo de proposta reescrito para a arquitetura atual, distinguindo Disparity Extender, wall following físico, temporizadores e nomes reais dos pacotes. Resultados históricos continuam identificados como históricos. |
| R25 | README do Raspberry antigo identifica o arquivo histórico e direciona ao workspace ativo. |
| R26 | Removidos conteúdo fictício de aprovação, ficha, agradecimentos e número de ordem; siglas, símbolos e metadados corrigidos; diagrama real incluído e estouros de margem corrigidos. |
| R27 | Removido entry point do visualizador PID inexistente. |

## Validação

- **1.151 testes distintos aprovados:** pesquisa 433, raiz/MCP 160, carro 547 e simulador 11. A execução central cobriu 431 testes de pesquisa; os dois testes adicionais de rastreamento de falha e dependência de proveniência passaram na execução focalizada final (17 testes, dos quais 15 já pertenciam à execução central). Não há dupla contagem no total.
- Carro: dois testes pulados e 24 excluídos pelo filtro explícito. Não são contados como aprovados.
- `verify --full`: camadas A, B, C e D aprovadas; C verificou seis invariantes. A camada E reprova **somente por worktree não commitada**. Essa condição foi preservada, sem contornar a checagem de proveniência.
- ROS2 Humble: oito pacotes do simulador compilados em diretório limpo de contêiner; integração real confirmou YAML, relógio, scan/odometria, geometria e parada por perda dos sensores.
- Driver VESC e mensagens compilados. Integração ROS com pseudo-terminal confirmou emissão de RPM 1200 quando autorizado e bloqueio do fluxo contínuo de solicitações após retirada ou expiração da habilitação, com potência nula na serial. Não foi usado hardware físico.
- Dissertação: compilação LaTeX concluída, **162 páginas, zero avisos Overfull**. Permanecem avisos Underfull e avisos de pacotes da distribuição TeX, sem falha de compilação. O PDF atualizado está em [dissertacao.pdf](../../dissertacao.pdf).
- `git diff --check`, sintaxe dos scripts shell e configuração Compose válidos.

Logs: [verificador central](verify-correcoes.log.txt), [regressões finais](regressoes-finais.log.txt), [compilação ROS](ros-build.log.txt), [integração ROS](ros-integracao.log.txt), [VESC](vesc-integracao.log.txt), [LaTeX](latex-correcoes.log.txt).

## Limites da validação

A operação autônoma, calibração física e gate de desempenho no Raspberry continuam exigindo medição no veículo. Os testes no host e no contêiner verificam os contratos de software; não constituem validação física. A imagem Docker já existente foi usada para a compilação isolada; não foi reconstruída integralmente a imagem base a partir de uma instalação vazia.

Foram examinados 19 relatórios históricos com voltas individuais: nenhum apresenta uma volta concluída seguida de colisão no mesmo passo. Entretanto, uma colisão descartada pelo código antigo na última volta não pode ser reconstruída desses artefatos. Nenhum resultado histórico foi alterado ou apresentado como reavaliado. A consulta está registrada em [historico_colisoes.json](historico_colisoes.json).

Durante a execução surgiram alterações paralelas em vários arquivos de `f1tenth_code_rasp`, além do índice CodeGraph. Foram preservadas. Minha alteração nesse repositório se limita ao README; as demais alterações paralelas não integram esta validação.

Ficha catalográfica, assinaturas e agradecimentos foram omitidos da versão de trabalho até existirem conteúdos reais; não foram inventados dados pessoais ou de aprovação.

## Publicação

Em 10/09/2026 o autor autorizou commit e push de todas as alterações pendentes na main, incluindo as alterações paralelas mencionadas acima. Os logs anteriores são registros históricos da validação antes do commit.
