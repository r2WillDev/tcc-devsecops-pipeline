# Etapa 5 — C1: Pipeline Baseline

> **Repositório:** [r2WillDev/tcc-devsecops-pipeline](https://github.com/r2WillDev/tcc-devsecops-pipeline)
> **Branch:** `feature/c1-baseline-pipeline`
> **Commits relacionados:** `0ef27c7`, `8cfe0f2`

---

## 🧭 Sumário

1. [Objetivo da Etapa](#1-objetivo-da-etapa)
2. [Relação com o Problema de Pesquisa](#2-relação-com-o-problema-de-pesquisa)
3. [Conceito de Pipeline Baseline](#3-conceito-de-pipeline-baseline)
4. [Escopo do C1](#4-escopo-do-c1)
5. [Decisão Técnica](#5-decisão-técnica)
6. [Arquivos Criados](#6-arquivos-criados)
7. [Funcionamento do Workflow](#7-funcionamento-do-workflow)
8. [Métricas Coletadas](#8-métricas-coletadas)
9. [Validações Manuais Realizadas](#9-validações-manuais-realizadas)
10. [Resultado Inicial do Workflow](#10-resultado-inicial-do-workflow)
11. [Próximos Passos](#11-próximos-passos)
12. [Observações Acadêmicas](#12-observações-acadêmicas)
13. [Resumo da Etapa](#13-resumo-da-etapa)

---

## 1. 🎯 Objetivo da Etapa

Esta etapa tem como objetivo a implementação do **Cenário C1 — Pipeline Baseline**, que representa a configuração mínima e funcional de um pipeline CI/CD sem a integração de qualquer ferramenta de análise de segurança.

O C1 cumpre o papel de **cenário de referência experimental** do trabalho de conclusão de curso. Todas as medições coletadas neste cenário serão utilizadas como base comparativa para os cenários subsequentes, que incorporarão progressivamente ferramentas de segurança ao pipeline.

Os objetivos específicos desta etapa são:

- Criar o arquivo de workflow do GitHub Actions para o C1;
- Implementar um script de medição de tempo para as etapas do pipeline;
- Gerar automaticamente um arquivo CSV com as métricas coletadas por execução;
- Validar manualmente o fluxo completo antes de automatizá-lo;
- Garantir a reprodutibilidade das execuções em ambiente controlado.

---

## 2. Relação com o Problema de Pesquisa

O problema de pesquisa deste TCC é:

> *Como a integração de ferramentas de análise de segurança — SAST, DAST e SCA — afeta o lead time em pipelines CI/CD, e como otimizar esse impacto?*

Para responder a essa pergunta de forma rigorosa, é necessário estabelecer uma **linha de base mensurável**. O C1 cumpre exatamente essa função: ao executar o pipeline sem nenhuma ferramenta de segurança, é possível determinar o tempo de execução natural do fluxo de entrega contínua.

A partir dos dados coletados no C1, será possível calcular, nos cenários seguintes, o **delta de tempo** introduzido por cada ferramenta de segurança, isolando o impacto de cada prática DevSecOps no lead time do pipeline.

---

## 3. Conceito de Pipeline Baseline

No contexto de experimentos controlados em engenharia de software, um **pipeline baseline** é aquele que executa apenas as etapas fundamentais de um fluxo CI/CD, sem acréscimos de ferramentas adicionais. Ele representa o estado mais simples e funcional do pipeline.

No contexto deste TCC, o C1 — Pipeline Baseline contempla:

| Incluído no C1 | Excluído do C1 |
|---|---|
| Checkout do código | SonarQube (SAST) |
| Instalação de dependências | Trivy (SCA) |
| Execução de testes unitários | OWASP ZAP (DAST) |
| Build da imagem Docker | Qualquer outra análise de segurança |
| Deploy no Kubernetes (kind) | |
| Smoke test no endpoint `/health` | |
| Coleta de métricas de tempo | |

Essa delimitação garante que o tempo medido no C1 reflita exclusivamente o custo do processo de entrega, sem interferência das práticas de segurança que serão avaliadas nos cenários seguintes.

---

## 4. Escopo do C1

O cenário C1 faz parte de uma série de cinco cenários experimentais planejados para o TCC:

| Cenário | Descrição |
|---|---|
| **C1** | Pipeline Baseline (sem segurança) — *esta etapa* |
| C2 | Baseline + SAST (SonarQube) |
| C3 | Baseline + SAST + SCA (Trivy) |
| C4 | Baseline + SAST + SCA + DAST (OWASP ZAP) |
| C5 | Pipeline Otimizado |

O C1 é o ponto de partida do experimento. Sem ele, não é possível quantificar o impacto de nenhuma das ferramentas de segurança nos cenários posteriores. Por isso, sua implementação e validação são etapas críticas para a integridade metodológica da pesquisa.

---

## 5. Decisão Técnica

### 5.1 Ambiente de Execução

O workflow C1 foi implementado utilizando **GitHub-hosted runner**, conforme configuração:

```yaml
runs-on: ubuntu-latest
```

Essa decisão foi tomada após análise das alternativas disponíveis. A tabela a seguir compara as duas abordagens principais:

| Critério | GitHub-hosted Runner | Self-hosted Runner |
|---|---|---|
| Reprodutibilidade | Alta — ambiente padronizado pelo GitHub | Média — depende da máquina local |
| Independência da máquina local | Sim | Não |
| Facilidade de repetição | Alta | Baixa (requer máquina disponível) |
| Complexidade de configuração inicial | Baixa | Alta |
| Adequação ao experimento | Recomendada | Não adotada nesta fase |

A escolha pelo GitHub-hosted runner garante que cada execução do workflow ocorra em um **ambiente isolado e equivalente**, condição essencial para a validade dos dados experimentais coletados.

### 5.2 Cluster Kubernetes Efêmero

O cluster Kubernetes utilizado neste workflow é criado com **kind** (*Kubernetes in Docker*) diretamente no runner do GitHub Actions, durante a execução do pipeline. Esse cluster possui natureza **efêmera**: é criado no início da execução e descartado automaticamente ao término, sem persistência entre execuções.

Essa abordagem foi adotada pelos seguintes motivos:

- Elimina a necessidade de um cluster externo permanente;
- Garante que cada execução parta de um estado limpo e previsível;
- Simplifica a configuração do ambiente experimental;
- Evita interferências entre execuções consecutivas.

A criação do cluster é automatizada dentro do próprio workflow, sem intervenção manual.

---

## 6. Arquivos Criados

Nesta etapa, foram criados os seguintes arquivos no repositório:

### 6.1 `.github/workflows/c1-baseline.yml`

Define o workflow do GitHub Actions para o cenário C1. Contém todas as etapas do pipeline, desde o checkout do código até o upload do CSV de métricas como artifact.

```
.github/
└── workflows/
    └── c1-baseline.yml
```

### 6.2 `ci/scripts/measure_step.sh`

Script Bash responsável por medir o tempo de execução das etapas principais do pipeline. O script registra o instante de início, executa a etapa correspondente e registra o instante de término, calculando a duração em segundos. O resultado é escrito no arquivo CSV de métricas.

```
ci/
└── scripts/
    └── measure_step.sh
```

### 6.3 `analysis/raw/c1_baseline.csv`

Arquivo-base que define o cabeçalho do CSV de resultados do cenário C1. Cada execução do workflow gera uma nova linha neste arquivo, que é então enviado como artifact ao GitHub Actions.

```
analysis/
└── raw/
    └── c1_baseline.csv
```

### 6.4 `.gitattributes`

Define a configuração de final de linha para os arquivos do repositório, forçando o uso de `LF` para arquivos `.sh`, `.yml` e `.yaml`. Essa configuração evita problemas de execução no ambiente Linux do GitHub Actions, que podem ocorrer quando arquivos são editados em sistemas Windows (que utilizam `CRLF` por padrão).

```
# .gitattributes
*.sh    text eol=lf
*.yml   text eol=lf
*.yaml  text eol=lf
```

---

## 7. Funcionamento do Workflow

O workflow `c1-baseline.yml` executa as seguintes etapas, na ordem indicada:

| # | Etapa | Descrição |
|---|---|---|
| 1 | **Checkout do código** | Clona o repositório na branch em execução |
| 2 | **Preparação do CSV** | Cria o arquivo CSV com o cabeçalho das métricas |
| 3 | **Configuração do Python 3.12** | Instala e configura o interpretador Python |
| 4 | **Permissão do script** | Concede permissão de execução ao `measure_step.sh` |
| 5 | **Instalação de dependências** | Instala as dependências Python via `pip` (medida) |
| 6 | **Testes unitários** | Executa os testes com Pytest (medida) |
| 7 | **Build da imagem Docker** | Constrói a imagem da aplicação (medida) |
| 8 | **Instalação do kind** | Baixa e instala o kind no runner |
| 9 | **Criação do cluster** | Inicializa o cluster Kubernetes local no runner |
| 10 | **Deploy no Kubernetes** | Aplica os manifests e aguarda o pod ficar disponível (medida) |
| 11 | **Smoke test** | Verifica a resposta do endpoint `/health` (medida) |
| 12 | **Tempo total** | Calcula e registra a duração total do workflow |
| 13 | **Exibição das métricas** | Imprime as métricas coletadas no log do workflow |
| 14 | **Resumo no GitHub Actions** | Escreve um resumo formatado na aba *Summary* do workflow |
| 15 | **Upload do CSV** | Envia o CSV como artifact para download posterior |

As etapas marcadas como **medidas** são aquelas cujo tempo de execução é registrado no CSV de métricas, conforme detalhado na seção seguinte.

---

## 8. Métricas Coletadas

### 8.1 Estrutura do CSV

O arquivo CSV gerado por cada execução segue o seguinte esquema:

```
scenario,run_id,run_number,commit_sha,step_name,start_timestamp,end_timestamp,duration_seconds,status
```

| Campo | Descrição |
|---|---|
| `scenario` | Identificador do cenário (`C1`) |
| `run_id` | ID único da execução no GitHub Actions |
| `run_number` | Número sequencial da execução |
| `commit_sha` | Hash do commit que disparou o workflow |
| `step_name` | Nome da etapa medida |
| `start_timestamp` | Instante de início da etapa (ISO 8601) |
| `end_timestamp` | Instante de término da etapa (ISO 8601) |
| `duration_seconds` | Duração em segundos |
| `status` | Status da etapa (`success` ou `failure`) |

### 8.2 Etapas Medidas

As seguintes etapas têm seu tempo de execução registrado no CSV:

| Etapa (`step_name`) | O que representa |
|---|---|
| `install_dependencies` | Instalação das dependências Python |
| `unit_tests` | Execução dos testes unitários com Pytest |
| `docker_build` | Build da imagem Docker da aplicação |
| `kubernetes_deploy` | Deploy no cluster kind e aguardo do pod |
| `kubernetes_smoke_test` | Verificação do endpoint `/health` |
| `workflow_total` | Duração total do workflow de ponta a ponta |

### 8.3 Resultado de uma Execução Inicial

A tabela a seguir apresenta os valores registrados em uma execução inicial do workflow C1, realizados para validação do pipeline:

| Etapa | Duração |
|---|---:|
| `install_dependencies` | 7s |
| `unit_tests` | 2s |
| `docker_build` | 14s |
| `kubernetes_deploy` | 28s |
| `kubernetes_smoke_test` | 5s |
| `workflow_total` | 83s |

> [!NOTE]
> Os valores acima são provenientes de uma execução inicial de validação e têm caráter ilustrativo. Os dados utilizados na análise estatística do TCC serão coletados nas **cinco execuções oficiais** planejadas para esta etapa. Esses resultados serão documentados posteriormente.

---

## 9. Validações Manuais Realizadas

Antes de automatizar o fluxo no GitHub Actions, todas as etapas do C1 foram validadas manualmente no ambiente local. Essa prática garante que eventuais problemas sejam identificados e corrigidos antes de consumir minutos de execução no runner remoto.

### 9.1 Checklist de Validação Local

| Item Validado | Status |
|---|---|
| Branch `feature/c1-baseline-pipeline` criada | Concluído |
| Arquivos da aplicação FastAPI presentes | Concluído |
| Arquivos Docker (`Dockerfile`, `docker-compose.yml`) presentes | Concluído |
| Manifests Kubernetes presentes | Concluído |
| Testes locais executando e passando | Concluído |
| Docker build local funcionando | Concluído |
| Cluster kind local recriado com sucesso | Concluído |
| `kubectl` acessando o cluster corretamente | Concluído |
| Deploy Kubernetes manual executado com sucesso | Concluído |
| Pod da aplicação em status `Running` | Concluído |
| Endpoint `/` respondendo corretamente | Concluído |
| Endpoint `/health` respondendo corretamente | Concluído |

### 9.2 Respostas dos Endpoints Validadas

**Endpoint raiz (`/`):**

```json
{"message": "TCC DevSecOps API"}
```

**Endpoint de saúde (`/health`):**

```json
{"status": "ok"}
```

A validação manual confirmou que a aplicação, a imagem Docker e os manifests Kubernetes estão funcionando corretamente, habilitando a automação segura do fluxo via GitHub Actions.

---

## 10. Resultado Inicial do Workflow

O workflow `C1 - Baseline Pipeline` foi executado com sucesso no GitHub Actions após a criação e os ajustes iniciais.

### 10.1 Commits Realizados

| Hash | Mensagem |
|---|---|
| `0ef27c7` | `ci: add baseline workflow for C1` |
| `8cfe0f2` | `ci: add total duration metric to C1 workflow` |

O segundo commit (`8cfe0f2`) foi necessário para incluir a métrica `workflow_total`, que registra a duração completa do workflow de ponta a ponta. Essa métrica é fundamental para a análise comparativa entre os cenários.

### 10.2 Status das Execuções Iniciais

A execução inicial confirmou o funcionamento correto do pipeline, com todas as etapas concluídas com sucesso e o CSV de métricas gerado e disponível como artifact.

> As **cinco execuções oficiais** do C1, destinadas à coleta dos dados experimentais do TCC, estão planejadas e serão realizadas na sequência desta validação. Os resultados serão consolidados conforme descrito na seção de próximos passos.

---

## 11. Próximos Passos

Após a validação inicial do workflow C1, as ações imediatas previstas são:

1. **Executar o workflow C1 pelo menos cinco vezes**, de forma independente, para garantir uma amostra representativa dos tempos de execução;
2. **Baixar os artifacts** gerados em cada execução a partir da interface do GitHub Actions;
3. **Salvar os CSVs** individuais de cada execução na estrutura de diretórios definida na seção anterior;
4. **Consolidar os resultados** em um único arquivo CSV para facilitar a análise;
5. **Calcular as estatísticas descritivas** para cada etapa medida: média, mínimo, máximo e coeficiente de variação;
6. **Utilizar os dados consolidados do C1 como base de comparação** para os cenários C2, C3, C4 e C5.

> **Importante:** O avanço para o próximo cenário (C2 — com SonarQube) somente deve ocorrer após a conclusão completa das cinco execuções oficiais do C1 e a consolidação dos dados coletados. Não devem ser iniciadas nesta etapa as implementações de SonarQube, Trivy ou OWASP ZAP.

---

## 12. Observações Acadêmicas

### 12.1 Validade Interna do Experimento

A coleta de múltiplas execuções do mesmo cenário é uma prática estabelecida em experimentos controlados de engenharia de software. O número mínimo de cinco execuções para o C1 visa mitigar variações causadas por fatores externos ao pipeline, como flutuações na disponibilidade de recursos do runner do GitHub Actions.

A análise do coeficiente de variação entre as execuções do C1 permitirá avaliar a **estabilidade do cenário baseline**, condição necessária para que as comparações com os cenários seguintes sejam estatisticamente válidas.

### 12.2 Rastreabilidade

Cada execução do workflow registra o `commit_sha` e o `run_id` no CSV de métricas. Essa informação garante **rastreabilidade total** entre os dados coletados e o estado exato do código e do ambiente em que foram produzidos.

### 12.3 Replicabilidade

A utilização do GitHub-hosted runner, combinada com a criação de um cluster Kubernetes efêmero via kind, garante que o ambiente de cada execução seja **equivalente e reprodutível**. Isso é um requisito fundamental para a validade dos dados experimentais e para a possibilidade de replicação do experimento por outros pesquisadores.

### 15.4 Limitações Conhecidas

- Os tempos de execução no GitHub-hosted runner podem apresentar variação em função da carga nos servidores do GitHub. Essa variação será mitigada pelo uso de estatísticas descritivas sobre múltiplas execuções.
- O cluster kind criado no runner é de nó único e não representa um ambiente Kubernetes de produção. Essa limitação é aceitável no contexto deste experimento, cujo foco é a comparação relativa entre cenários, e não a avaliação de desempenho em escala.

---

## 13. Resumo da Etapa

O **Cenário C1 — Pipeline Baseline** estabelece a **linha de base experimental** do trabalho de conclusão de curso. Nesta etapa, foi implementado um pipeline CI/CD completo e funcional, abrangendo as etapas de teste, containerização e deploy em Kubernetes, sem a adição de qualquer ferramenta de análise de segurança.

A principal contribuição desta etapa para a pesquisa é a definição de um **tempo de referência mensurável e reprodutível**, a partir do qual será possível quantificar, com rigor, o impacto de cada prática DevSecOps introduzida nos cenários seguintes. Sem o C1, não seria possível isolar a contribuição individual de ferramentas como SonarQube, Trivy e OWASP ZAP no lead time do pipeline.

Os dados coletados nas cinco execuções oficiais do C1 formarão o conjunto de referência que fundamentará as análises comparativas de toda a pesquisa experimental.

---

*Documento gerado como parte da documentação técnica do TCC:*
**"Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD"**