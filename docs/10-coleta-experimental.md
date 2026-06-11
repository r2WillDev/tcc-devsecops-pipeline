# Etapa 10 — Coleta Experimental

Documentação da coleta experimental do TCC **Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD**.

- **Repositório:** [`github.com/r2WillDev/tcc-devsecops-pipeline`](https://github.com/r2WillDev/tcc-devsecops-pipeline)
- **Branch da etapa:** `analysis/results-v1`
- **Documento:** `docs/10-coleta-experimental.md`

> [!NOTE]
> Esta etapa documenta a **coleta experimental** dos dados de execução dos pipelines, ou seja, a organização, normalização e validação dos CSVs brutos gerados pelos workflows. Ela **não** corresponde à análise final dos resultados, que será conduzida no capítulo de resultados do TCC. Os números apresentados aqui servem apenas como validação inicial da integridade da coleta.

---

## 1. Objetivo da etapa

O objetivo geral do TCC é desenvolver e avaliar um pipeline DevSecOps otimizado para minimizar o impacto no tempo de deploy de uma aplicação containerizada. A pergunta principal que orienta esta etapa de coleta é:

> **Quanto tempo cada camada de segurança adicionou ao pipeline CI/CD?**

Para responder a essa pergunta de forma rigorosa, é necessário primeiro consolidar um dataset confiável, rastreável e validado. A Etapa 10 cumpre exatamente esse papel: transformar os artifacts brutos dos workflows do GitHub Actions em um dataset único e tratado, pronto para a análise acadêmica posterior.[^1]

---

## 2. Cenários experimentais

Os cinco cenários experimentais representam o acréscimo incremental de camadas de segurança sobre um pipeline baseline.

| Cenário | Descrição                                       | Ferramentas                                   |
| ------- | ----------------------------------------------- | --------------------------------------------- |
| C1      | Pipeline baseline, sem ferramentas de segurança | Nenhuma                                       |
| C2      | Pipeline com SAST                               | SonarQube                                     |
| C3      | Pipeline com SAST + SCA                         | SonarQube + Trivy                             |
| C4      | Pipeline com SAST + SCA + DAST                  | SonarQube + Trivy + OWASP ZAP                 |
| C5      | Pipeline otimizado                              | SonarQube + Trivy + OWASP ZAP com otimizações |

> [!IMPORTANT]
> A métrica principal de lead time é `workflow_total`. Todas as comparações entre cenários — overhead absoluto, overhead percentual e impacto incremental de cada camada — derivam dessa métrica.[^1]

---

## 3. O que foi realizado na Etapa 10

A Etapa 10 — Coleta experimental foi executada com os seguintes objetivos:

1. organizar os CSVs brutos dos artifacts dos workflows;
2. separar dados de tempo e dados de segurança;
3. garantir 5 execuções válidas por cenário;
4. validar colunas obrigatórias;
5. validar presença de `workflow_total`;
6. validar que `duration_seconds` é numérico;
7. validar que todos os status são `success`;
8. gerar o dataset consolidado `analysis/processed/results_normalized.csv`;
9. criar o script `ci/scripts/normalize_results.py`;
10. documentar a estrutura em `analysis/README.md`.

O script `normalize_results.py` lê os CSVs em `analysis/raw/<cenario>/timing` e gera `analysis/processed/results_normalized.csv`, aplicando as validações descritas na [seção 7](#7-validação-realizada).

---

## 4. Estrutura final dos dados

A organização do diretório `analysis/` separa explicitamente dados brutos (`raw/`) de dados tratados (`processed/`), preservando a rastreabilidade da origem de cada métrica.

```text
analysis/
  raw/
    c1/
      timing/
    c2/
      timing/
    c3/
      timing/
      security/
    c4/
      timing/
      security/
    c5/
      timing/
      security/
  processed/
    results_normalized.csv
```

Significado de cada elemento da estrutura:

- `timing`: CSVs principais de tempo por execução, contendo a duração de cada etapa do workflow, incluindo a linha `workflow_total`;
- `security`: summaries das ferramentas de segurança (Trivy e OWASP ZAP), quando aplicável ao cenário;
- `processed`: dataset tratado e consolidado, derivado dos dados brutos;
- `results_normalized.csv`: dataset final, normalizado e validado, utilizado como entrada única para a análise acadêmica.

---

## 5. Dados brutos coletados

Os dados brutos foram baixados diretamente dos artifacts dos workflows do GitHub Actions e organizados por cenário e por tipo (tempo ou segurança).

| Caminho                    | Quantidade | Finalidade                |
| -------------------------- | ---------: | ------------------------- |
| `analysis/raw/c1/timing`   |     5 CSVs | Métricas de tempo do C1   |
| `analysis/raw/c2/timing`   |     5 CSVs | Métricas de tempo do C2   |
| `analysis/raw/c3/timing`   |     5 CSVs | Métricas de tempo do C3   |
| `analysis/raw/c3/security` |     5 CSVs | Resumos Trivy do C3       |
| `analysis/raw/c4/timing`   |     5 CSVs | Métricas de tempo do C4   |
| `analysis/raw/c4/security` |    10 CSVs | Resumos Trivy e ZAP do C4 |
| `analysis/raw/c5/timing`   |     5 CSVs | Métricas de tempo do C5   |
| `analysis/raw/c5/security` |    10 CSVs | Resumos Trivy e ZAP do C5 |

> [!WARNING]
> Os tempos coletados são sensíveis às condições do ambiente. Diferenças entre **cache frio e cache quente**, carga do runner local, processos concorrentes e variações de rede ou de inicialização de containers podem introduzir ruído nas medições.[^2] Por isso, o estado de cache e a carga do runner devem ser observados durante toda a coleta.

> [!NOTE]
> As métricas de segurança em `security/` complementam a análise, mas não substituem as métricas de tempo: elas servem para caracterizar o que cada ferramenta detectou, não para medir o lead time do pipeline.[^5]

---

## 6. Dataset consolidado

A normalização gerou o arquivo `analysis/processed/results_normalized.csv` com as seguintes características:

- 235 linhas;
- 19 colunas;
- 25 execuções principais;
- 5 execuções válidas por cenário;
- todos os status `success`;
- nenhuma duração inválida;
- 25 linhas `workflow_total`.

### 6.1 Colunas principais do dataset

| Coluna               | Descrição                                                           |
| -------------------- | ------------------------------------------------------------------- |
| `scenario_key`       | Identificador curto do cenário, como `c1`, `c2`, `c3`, `c4` ou `c5` |
| `scenario_order`     | Ordem numérica do cenário                                           |
| `scenario_label`     | Nome descritivo do cenário                                          |
| `security_layer`     | Camada de segurança representada pelo cenário                       |
| `run_index`          | Índice local da execução dentro do cenário                          |
| `source_file`        | Caminho do CSV bruto usado como origem                              |
| `scenario`           | Nome original do cenário registrado no CSV                          |
| `run_id`             | Identificador da execução do workflow                               |
| `run_number`         | Número da execução do workflow                                      |
| `commit_sha`         | Commit associado à execução                                         |
| `step_name`          | Nome da etapa medida                                                |
| `start_timestamp`    | Início da etapa                                                     |
| `end_timestamp`      | Fim da etapa                                                        |
| `duration_seconds`   | Duração da etapa em segundos                                        |
| `status`             | Status da etapa                                                     |
| `is_workflow_total`  | Indica se a linha representa o tempo total do workflow              |
| `is_security_step`   | Indica se a etapa pertence à camada de segurança                    |
| `is_deploy_step`     | Indica se a etapa pertence ao deploy ou smoke test                  |
| `is_valid_execution` | Indica se a execução foi considerada válida                         |

Uma prévia do formato CSV consolidado pode ser representada da seguinte forma:

```csv
scenario_key,scenario_order,scenario_label,run_index,step_name,duration_seconds,status,is_workflow_total,is_valid_execution
c1,1,C1 - Baseline,1,workflow_total,87,success,True,True
c2,2,C2 - SAST,1,workflow_total,88,success,True,True
c3,3,C3 - SAST + SCA,1,workflow_total,127,success,True,True
```

---

## 7. Validação realizada

A validação automática executada pelo script `normalize_results.py` confirmou os seguintes critérios:

| Critério                                        | Resultado |
| ----------------------------------------------- | --------- |
| Colunas obrigatórias presentes                  | Aprovado  |
| `workflow_total` presente em todas as execuções | Aprovado  |
| `duration_seconds` numérico                     | Aprovado  |
| Todos os status como `success`                  | Aprovado  |
| Nenhuma execução inválida sinalizada            | Aprovado  |
| 5 execuções válidas por cenário                 | Aprovado  |
| 25 linhas `workflow_total`                      | Aprovado  |

Resultado final emitido pelo script:

```text
DATASET NORMALIZADO APROVADO PARA ANALISE.
```

---

## 8. Resumo estatístico inicial

A tabela a seguir apresenta um resumo descritivo das durações de `workflow_total` por cenário, com base nas 5 execuções válidas de cada um.

| Cenário                | Execuções |  Média | Mediana | Mínimo | Máximo | Desvio padrão |
| ---------------------- | --------: | -----: | ------: | -----: | -----: | ------------: |
| C1 - Baseline          |         5 |  87.0s |   87.0s |    80s |    93s |          5.61 |
| C2 - SAST              |         5 |  90.4s |   88.0s |    79s |   108s |         10.69 |
| C3 - SAST + SCA        |         5 | 126.2s |  127.0s |   107s |   149s |         16.02 |
| C4 - SAST + SCA + DAST |         5 | 236.6s |  207.0s |   197s |   309s |         49.67 |
| C5 - Optimized         |         5 | 191.8s |  180.0s |   172s |   240s |         27.63 |

> [!NOTE]
> Esta tabela é uma **validação inicial da coleta**, não a análise final completa do capítulo de resultados. Os valores confirmam que o dataset está consistente e que há variabilidade esperada entre cenários, mas as conclusões sobre o impacto de cada camada serão desenvolvidas no capítulo de resultados.

---

## 9. Commits realizados na etapa

| Commit    | Mensagem                                        | Finalidade                                  |
| --------- | ----------------------------------------------- | ------------------------------------------- |
| `dd23c1f` | `analysis: add raw experimental run data`       | Adicionar dados brutos experimentais        |
| `3a2abe9` | `analysis: organize raw experimental data`      | Reorganizar dados brutos por cenário e tipo |
| `e7b10cb` | `analysis: add normalized experimental results` | Adicionar script e dataset normalizado      |
| `8620e6d` | `docs: document analysis data structure`        | Documentar estrutura da pasta `analysis`    |

---

## 10. Comandos executados ou relevantes

> [!TIP]
> Para reproduzir a geração do dataset, execute os comandos abaixo a partir da raiz do repositório, com a branch `analysis/results-v1` ativa e o ambiente Python com `pandas` instalado.

### 10.1 Validar estado da branch

```powershell
git status
git log --oneline -6
```

### 10.2 Rodar normalização

```powershell
python .\ci\scripts\normalize_results.py
```

### 10.3 Validar dataset rapidamente

```powershell
python -c "import pandas as pd; df = pd.read_csv('analysis/processed/results_normalized.csv'); w = df[df['is_workflow_total'] == True]; print(w.groupby(['scenario_key','scenario_label'])['duration_seconds'].agg(['count','mean','median','min','max','std']).round(2).to_string())"
```

### 10.4 Commit sugerido para este documento

```bash
git add docs/10-coleta-experimental.md
git commit -m "docs: document experimental data collection"
```

---

## 11. Critérios de execução válida

Uma execução foi considerada **válida** somente quando todas as condições a seguir foram satisfeitas:

1. o CSV possui as colunas obrigatórias;
2. existe uma linha `workflow_total`;
3. `duration_seconds` é numérico;
4. o status é `success`;
5. a execução pertence a C1, C2, C3, C4 ou C5;
6. o arquivo bruto foi preservado e rastreável via `source_file`.

A adoção de 5 execuções por cenário como mínimo aceitável equilibra a redução do efeito de variações pontuais com a viabilidade dentro do prazo do TCC.[^3]

---

## 12. Critérios de exclusão ou sinalização

> [!CAUTION]
> Execuções com falha ou inconsistentes **não devem ser misturadas** com execuções válidas. Caso sejam mantidas para fins de registro, devem ser claramente sinalizadas e excluídas dos cálculos estatísticos.[^4]

Uma execução deve ser excluída ou sinalizada quando apresentar qualquer um dos problemas:

- workflow com status `failure`;
- CSV vazio ou contendo apenas cabeçalho;
- ausência de `workflow_total`;
- `duration_seconds` inválido;
- cenário incorreto ou não identificado;
- execução de teste/rascunho;
- execução feita em condição muito diferente sem documentação.

---

## 13. Condições controladas

Para reduzir o ruído experimental, as comparações buscaram manter as seguintes condições controladas:

- mesma máquina ou runner, quando possível;
- mesmo repositório;
- branch controlada;
- aplicação sem alterações funcionais durante a coleta;
- mesmos workflows por cenário;
- mesmas ferramentas de segurança;
- dados brutos preservados;
- execução sem processos pesados concorrentes, quando possível;
- atenção à diferença entre cache frio e cache quente.

---

## 14. Estratégia de coleta adotada

A estratégia adotada foi baseada em **artifacts baixados manualmente** do GitHub Actions e organizados no repositório, sob a estrutura descrita na [seção 4](#4-estrutura-final-dos-dados).

Essa escolha foi justificada por:

- simplicidade;
- rastreabilidade;
- baixo risco de complexidade da API;
- facilidade de auditoria;
- melhor adequação ao prazo do TCC;
- possibilidade de automatização futura com GitHub API ou GitHub CLI.

Comparação entre as estratégias avaliadas:

| Estratégia        | Vantagens                       | Desvantagens                             | Decisão                |
| ----------------- | ------------------------------- | ---------------------------------------- | ---------------------- |
| Artifacts manuais | Simples, auditável, direto      | Menos automatizado                       | Escolhida              |
| GitHub CLI        | Automatizável, útil para escala | Exige autenticação e comandos adicionais | Possível evolução      |
| GitHub REST API   | Mais automatizável e robusta    | Maior complexidade                       | Não usada nesta versão |

---


## 15. Riscos de validade

Esta seção registra os riscos de validade de forma transparente, sem enfraquecer o trabalho:

- poucas execuções podem limitar a generalização dos resultados;
- o cache pode impactar os tempos medidos;
- o C4 tende a variar mais por causa do DAST;
- o ambiente local pode introduzir ruído;
- rede, containers e Kubernetes podem variar entre execuções;
- as ferramentas de segurança podem ter tempos diferentes conforme cache, banco de dados e inicialização.

Esses riscos foram mitigados com:

- 5 execuções por cenário;
- preservação dos dados brutos;
- separação entre dados brutos e tratados;
- validação automática;
- critérios explícitos de execução válida;
- commits rastreáveis.

---

## 16. Limitações

As limitações desta etapa são registradas de forma acadêmica:

- estudo conduzido em ambiente controlado/local;
- amostra mínima de 5 execuções por cenário;
- resultados dependem da configuração do runner;
- não foram feitas inferências estatísticas avançadas nesta etapa;
- esta etapa prepara os dados, mas não substitui a análise final;
- os tempos representam este projeto, estes workflows e esta configuração experimental.

---

## 17. Relação com o capítulo de resultados

O dataset final `results_normalized.csv` permitirá calcular, no capítulo de resultados:

- tempo total por cenário;
- tempo médio por etapa;
- overhead absoluto;
- overhead percentual;
- impacto incremental do SAST;
- impacto incremental do SCA;
- impacto incremental do DAST;
- comparação entre C4 e C5;
- identificação de gargalos;
- tabelas e gráficos do capítulo de resultados.

Em particular, os dados permitem **comparar C4 e C5** de forma controlada, sem que esta etapa estabeleça conclusões finais sobre qual configuração é preferível em todos os contextos.

---

## 18. Arquivos relacionados

- [`analysis/README.md`](../analysis/README.md)
- [`analysis/processed/results_normalized.csv`](../analysis/processed/results_normalized.csv)
- [`analysis/raw`](../analysis/raw)
- [`ci/scripts/normalize_results.py`](../ci/scripts/normalize_results.py)

---


## Notas de rodapé

[^1]: `workflow_total` é a métrica que representa a duração total de uma execução completa do workflow, do início ao fim, em segundos. É a referência principal de lead time do pipeline e a base de todas as comparações de overhead entre cenários.

[^2]: Cache frio ocorre quando dependências, imagens ou bancos de dados das ferramentas ainda não estão disponíveis localmente e precisam ser baixados ou reconstruídos, aumentando o tempo de execução. Cache quente ocorre quando esses artefatos já estão presentes e podem ser reutilizados, reduzindo o tempo. A diferença entre os dois estados pode afetar diretamente as medições de tempo.

[^3]: Adotou-se o mínimo de 5 execuções por cenário por equilibrar dois fatores: reduzir o efeito de variações pontuais e outliers sobre as estatísticas descritivas, e manter a coleta viável dentro do prazo e dos recursos disponíveis para o TCC. Trata-se de um mínimo aceitável, não de um tamanho amostral para inferência estatística avançada.

[^4]: Execuções com falha (`failure`), CSVs incompletos ou cenários não identificados representam medições não comparáveis com as execuções válidas. Misturá-las distorceria médias, medianas e desvios padrão. Por isso, devem ser excluídas dos cálculos ou explicitamente sinalizadas para preservar a integridade do dataset.

[^5]: As métricas de segurança (resumos do Trivy e do OWASP ZAP) caracterizam o que cada ferramenta detectou — como número de vulnerabilidades por severidade — e complementam a análise de tempo. Elas ajudam a contextualizar o custo de cada camada, mas não substituem `workflow_total` nem as demais métricas de duração na avaliação do lead time.