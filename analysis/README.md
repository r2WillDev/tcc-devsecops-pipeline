# Analysis

Documentação da pasta `analysis`, que reúne os dados experimentais utilizados no TCC **Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD**.

Branch de trabalho atual: `analysis/results-v1`.

## Objetivo

A pasta `analysis` armazena os dados **brutos**, **tratados** e **consolidados** usados para a análise experimental do TCC. Ela concentra todo o material necessário para reproduzir as medições de lead time e a coleta de métricas de segurança, mantendo a separação entre os artefatos extraídos diretamente do GitHub Actions e o dataset final preparado para a análise estatística.

> [!NOTE]
> **Dados brutos** são os CSVs extraídos diretamente dos artifacts dos workflows, em `analysis/raw`. **Dados tratados** são o resultado da normalização, em `analysis/processed`. Os dados brutos nunca são editados manualmente: eles são preservados como evidência e servem de entrada para o script de normalização.

## Contexto do experimento

O TCC investiga **como a inclusão progressiva de práticas DevSecOps impacta o lead time de pipelines CI/CD**. A coleta de dados foi desenhada para responder, de forma mensurável, a uma pergunta central:

**Quanto tempo cada camada de segurança adicionou ao pipeline CI/CD?**

Para isso, partimos de um pipeline baseline (sem segurança) e adicionamos, de forma incremental, SAST, SCA e DAST, comparando o lead time de cada cenário. Um último cenário aplica otimizações sobre o pipeline mais completo para avaliar quanto do custo introduzido pode ser recuperado.

## Cenários avaliados

| Cenário | Descrição                                       | Ferramentas de segurança          | Tipo de dado coletado |
| ------- | ----------------------------------------------- | --------------------------------- | --------------------- |
| C1      | Pipeline baseline, sem ferramentas de segurança | Nenhuma                           | `timing`              |
| C2      | Pipeline com SAST                               | SonarQube                         | `timing`              |
| C3      | Pipeline com SAST + SCA                         | SonarQube, Trivy                  | `timing`, `security`  |
| C4      | Pipeline com SAST + SCA + DAST                  | SonarQube, Trivy, OWASP ZAP       | `timing`, `security`  |
| C5      | Pipeline otimizado                              | SonarQube, Trivy, OWASP ZAP       | `timing`, `security`  |

## Estrutura da pasta

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

A quantidade de arquivos por diretório está descrita abaixo:

| Caminho                    | Quantidade |
| -------------------------- | ---------: |
| `analysis/raw/c1/timing`   |     5 CSVs |
| `analysis/raw/c2/timing`   |     5 CSVs |
| `analysis/raw/c3/timing`   |     5 CSVs |
| `analysis/raw/c3/security` |     5 CSVs |
| `analysis/raw/c4/timing`   |     5 CSVs |
| `analysis/raw/c4/security` |    10 CSVs |
| `analysis/raw/c5/timing`   |     5 CSVs |
| `analysis/raw/c5/security` |    10 CSVs |

## Dados brutos

A pasta `analysis/raw` contém os dados brutos extraídos dos **artifacts dos workflows do GitHub Actions**. Cada cenário (C1 a C5) possui seu próprio subdiretório, e dentro de cada cenário os dados são separados por tipo: `timing` e, quando aplicável, `security`.

Esses arquivos são preservados exatamente como foram coletados. Eles não são editados manualmente e funcionam como entrada para o script de normalização, garantindo rastreabilidade entre o dataset final e a origem de cada medição.

### Timing

A pasta `timing` contém os CSVs principais de tempo de execução dos pipelines. Cada CSV corresponde a uma execução do workflow e registra a duração de cada etapa, incluindo a etapa `workflow_total`, que representa o tempo total do pipeline.[^workflow-total]

A métrica de lead time deste TCC é extraída exatamente desses arquivos. Por isso, todos os cenários (C1 a C5) possuem a pasta `timing` com 5 CSVs, um para cada execução válida.

### Security

A pasta `security` contém os summaries das ferramentas de segurança aplicáveis a cada cenário, como **Trivy** (SCA) e **OWASP ZAP** (DAST). Esses arquivos só existem nos cenários que incluem as camadas correspondentes:

- C1 e C2 não possuem pasta `security`, pois C1 não usa segurança e C2 usa apenas SAST via SonarQube (cuja análise não gera summary CSV nesta coleta);
- C3 possui 5 CSVs de `security`, referentes ao SCA (Trivy);
- C4 e C5 possuem 10 CSVs de `security` cada, referentes a SCA (Trivy) e DAST (OWASP ZAP).

> [!IMPORTANT]
> A métrica **principal de lead time** é `workflow_total`. Os summaries de segurança complementam a análise — quantos e quais achados cada ferramenta produziu — mas **não substituem** as métricas de tempo.[^security-complementa]

## Dados tratados

A pasta `analysis/processed` contém o dataset tratado e consolidado a partir dos CSVs brutos de `timing`. O arquivo gerado é:

```text
analysis/processed/results_normalized.csv
```

Esse é o **dataset principal para a análise estatística**. Ele unifica, em um único arquivo tabular, todas as execuções de todos os cenários, com colunas padronizadas que permitem agrupar, comparar e calcular métricas de forma direta. Características atuais:

- 235 linhas;
- 19 colunas;
- 25 execuções principais, sendo 5 por cenário;
- todos os status como `success`;
- nenhuma duração inválida;
- 25 linhas com `workflow_total` (uma por execução).

## Script de normalização

O arquivo `ci/scripts/normalize_results.py` é responsável por gerar o dataset consolidado. Ele lê os CSVs de tempo em `analysis/raw/<cenario>/timing`, padroniza colunas, classifica cada etapa (etapa total, etapa de segurança, etapa de deploy), associa metadados de cenário e produz o arquivo `analysis/processed/results_normalized.csv`.

Em outras palavras: o script `normalize_results.py` lê os arquivos em `analysis/raw/c1/timing`, `analysis/raw/c2/timing`, `analysis/raw/c3/timing`, `analysis/raw/c4/timing` e `analysis/raw/c5/timing`, e gera o arquivo `analysis/processed/results_normalized.csv`.

Comando para executar:

```powershell
python .\ci\scripts\normalize_results.py
```

Entradas lidas pelo script:

```text
analysis/raw/c1/timing
analysis/raw/c2/timing
analysis/raw/c3/timing
analysis/raw/c4/timing
analysis/raw/c5/timing
```

Saída gerada:

```text
analysis/processed/results_normalized.csv
```

## Critérios de execução válida

Uma execução é considerada **válida** quando satisfaz todos os critérios abaixo:

1. possui as colunas obrigatórias do CSV de timing;
2. possui a etapa `workflow_total`;
3. possui `duration_seconds` numérico;
4. possui status `success`;
5. pertence a um dos cenários C1, C2, C3, C4 ou C5;
6. não apresenta falhas no workflow.

Foram consideradas **5 execuções válidas por cenário**, totalizando **25 execuções principais**.[^cinco-execucoes]

> [!CAUTION]
> Execuções com falha **não devem ser misturadas** com execuções válidas sem sinalização explícita. Misturar runs falhos com runs bem-sucedidos contamina as estatísticas de tempo e compromete a comparação entre cenários. Caso uma execução inválida seja mantida no repositório por motivo de auditoria, ela deve ficar claramente identificada e fora do dataset normalizado.

## Dataset consolidado

O arquivo `results_normalized.csv` possui 19 colunas. As colunas principais são descritas a seguir:

| Coluna                | Descrição                                                                 |
| --------------------- | ------------------------------------------------------------------------- |
| `scenario_key`        | Identificador curto do cenário (ex.: `c1`, `c2`, `c3`, `c4`, `c5`).       |
| `scenario_order`      | Ordem numérica do cenário, usada para ordenar resultados.                 |
| `scenario_label`      | Rótulo legível do cenário (ex.: `C1 - Baseline`).                         |
| `security_layer`      | Camada(s) de segurança presente(s) no cenário (ex.: SAST, SCA, DAST).     |
| `run_index`           | Índice da execução dentro do cenário (1 a 5).                             |
| `source_file`         | Nome do CSV bruto de origem, garantindo rastreabilidade.                  |
| `scenario`            | Identificação do cenário conforme registrado no dado bruto.              |
| `run_id`              | Identificador da execução do workflow no GitHub Actions.                  |
| `run_number`          | Número sequencial do run no GitHub Actions.                               |
| `commit_sha`          | SHA do commit que disparou a execução.                                    |
| `step_name`           | Nome da etapa do pipeline registrada na linha.                            |
| `start_timestamp`     | Timestamp de início da etapa.                                             |
| `end_timestamp`       | Timestamp de término da etapa.                                            |
| `duration_seconds`    | Duração da etapa em segundos (numérico).                                  |
| `status`              | Status da etapa/execução (ex.: `success`).                               |
| `is_workflow_total`   | Sinaliza se a linha representa a etapa `workflow_total`.                  |
| `is_security_step`    | Sinaliza se a etapa é de uma ferramenta de segurança.                     |
| `is_deploy_step`      | Sinaliza se a etapa é de deploy (ex.: deploy no Kubernetes).             |
| `is_valid_execution`  | Sinaliza se a execução atende a todos os critérios de validade.          |

## Resumo da coleta

Resumo estatístico inicial da métrica `workflow_total` por cenário:

| Cenário                | Execuções |  Média | Mediana | Mínimo | Máximo | Desvio padrão |
| ---------------------- | --------: | -----: | ------: | -----: | -----: | ------------: |
| C1 - Baseline          |         5 |  87.0s |   87.0s |    80s |    93s |          5.61 |
| C2 - SAST              |         5 |  90.4s |   88.0s |    79s |   108s |         10.69 |
| C3 - SAST + SCA        |         5 | 126.2s |  127.0s |   107s |   149s |         16.02 |
| C4 - SAST + SCA + DAST |         5 | 236.6s |  207.0s |   197s |   309s |         49.67 |
| C5 - Optimized         |         5 | 191.8s |  180.0s |   172s |   240s |         27.63 |

> [!NOTE]
> Os valores acima refletem o estado atual da coleta e servem como referência para a etapa de análise estatística. Nenhuma conclusão interpretativa final é apresentada neste README.

## Cuidados metodológicos

Para preservar a comparabilidade entre cenários, os seguintes cuidados foram adotados durante a coleta:

- manter a **mesma máquina / mesmo runner** sempre que possível, reduzindo variação de hardware;
- **evitar alterar o código da aplicação** durante a coleta, para que as diferenças de tempo reflitam as camadas de segurança e não mudanças funcionais;
- **evitar processos pesados** na máquina durante as execuções, para não competir por CPU, memória e I/O;
- **diferenciar cache frio e cache quente**, registrando quando aplicável a condição da execução;[^cache]
- **não misturar falhas com execuções válidas**, conforme os critérios de validade;
- **documentar limitações** que possam afetar a interpretação dos tempos.

> [!WARNING]
> Cache frio versus cache quente, carga concorrente no runner e execução de processos pesados podem inflar ou reduzir artificialmente o `duration_seconds` de etapas e do `workflow_total`. Esses fatores devem ser controlados durante a coleta e considerados na análise.

## Como reproduzir

Para reproduzir a geração do dataset consolidado a partir dos dados brutos versionados:

```powershell
git checkout analysis/results-v1
python .\ci\scripts\normalize_results.py
```

Para uma validação rápida da quantidade de execuções por cenário (esperado: 5 por cenário):

```powershell
python -c "import pandas as pd; df = pd.read_csv('analysis/processed/results_normalized.csv'); print(df.groupby('scenario_key')['run_index'].nunique())"
```

## Como usar estes dados no TCC

O dataset `results_normalized.csv` foi estruturado para permitir o cálculo direto das métricas necessárias ao capítulo de resultados. A partir dele, é possível calcular:

- tempo total por cenário (a partir de `workflow_total`);
- tempo médio por etapa (`step_name` + `duration_seconds`);
- overhead absoluto entre cenários (ex.: C2 menos C1);
- overhead percentual entre cenários;
- impacto de SAST (C2 em relação a C1);
- impacto de SCA (C3 em relação a C2);
- impacto de DAST (C4 em relação a C3);
- comparação entre C4 e C5, avaliando o efeito das otimizações.

> [!IMPORTANT]
> Ao montar rankings de etapas operacionais (qual etapa consome mais tempo), a etapa `workflow_total` **não deve ser incluída**, pois ela representa o tempo total do workflow e não uma etapa operacional. Use `is_workflow_total` para filtrá-la quando necessário.

## Limitações

As limitações abaixo são registradas de forma transparente e não invalidam o experimento; elas delimitam o escopo das conclusões:

- a coleta utiliza **5 execuções por cenário**, quantidade mínima aceitável para análise comparativa, mas ainda sujeita a variância;
- pode haver **variação do ambiente local** (CPU, memória, I/O) entre execuções;
- o **cache** (frio ou quente) influencia os tempos observados;
- há **diferença entre o tempo de uma ferramenta** isolada e o **tempo total do workflow**, que inclui etapas adicionais como build e deploy;
- existe **variação natural** de containers, rede local e cluster Kubernetes que pode afetar o `duration_seconds`.

## Arquivos relacionados

- [`ci/scripts/normalize_results.py`](../ci/scripts/normalize_results.py) — script de normalização que gera o dataset consolidado.
- [`analysis/processed/results_normalized.csv`](processed/results_normalized.csv) — dataset consolidado para análise estatística.
- [`analysis/raw`](raw) — dados brutos extraídos dos artifacts do GitHub Actions.



[^workflow-total]: `workflow_total` é a etapa que representa o **tempo total do workflow**, ou seja, o lead time completo do pipeline da disparada até a conclusão. É a métrica principal deste TCC. Por representar o todo, não deve ser tratada como uma etapa operacional em rankings de etapas.

[^cache]: **Cache frio** ocorre quando dependências, imagens de container ou bancos de dados de ferramentas precisam ser baixados/reconstruídos do zero, aumentando o tempo. **Cache quente** ocorre quando esses artefatos já estão disponíveis localmente, reduzindo o tempo. A condição de cache deve ser controlada para evitar comparações injustas entre execuções.

[^cinco-execucoes]: Cinco execuções por cenário é adotado como **mínimo aceitável** porque permite calcular média, mediana, mínimo, máximo e desvio padrão de forma significativa, reduzindo o peso de uma execução atípica isolada. É um ponto de equilíbrio entre custo de coleta e robustez estatística para um experimento controlado neste escopo.

[^security-complementa]: As métricas de segurança (número e severidade de achados do Trivy e do OWASP ZAP) **complementam** a análise de lead time ao descrever o que cada camada entrega, mas **não substituem** as métricas de tempo. A pergunta central do experimento é sobre o impacto no lead time, e por isso as métricas de tempo permanecem como referência primária da análise.