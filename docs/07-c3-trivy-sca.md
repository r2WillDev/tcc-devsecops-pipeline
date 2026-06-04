 # Etapa 7 — C3: Pipeline com SAST + SCA usando Trivy

## Sumário

- [1. Objetivo da etapa](#1-objetivo-da-etapa)
- [2. Contexto experimental](#2-contexto-experimental)
- [3. Conceitos principais](#3-conceitos-principais)
  - [3.1 SAST](#31-sast)
  - [3.2 SCA](#32-sca)
  - [3.3 Trivy](#33-trivy)
  - [3.4 CVE e severidade](#34-cve-e-severidade)
- [4. Escopo do cenário C3](#4-escopo-do-cenário-c3)
- [5. Arquivos criados ou modificados](#5-arquivos-criados-ou-modificados)
- [6. Funcionamento do workflow C3](#6-funcionamento-do-workflow-c3)
- [7. Configuração do Trivy](#7-configuração-do-trivy)
- [8. Métricas coletadas](#8-métricas-coletadas)
- [9. Resultados das execuções](#9-resultados-das-execuções)
- [10. Vulnerabilidades encontradas](#10-vulnerabilidades-encontradas)
- [11. Problemas encontrados e correções](#11-problemas-encontrados-e-correções)
- [12. Evidências recomendadas](#12-evidências-recomendadas)
- [13. Limitações metodológicas](#13-limitações-metodológicas)
- [14. Critério de conclusão](#14-critério-de-conclusão)
- [15. Próximos passos](#15-próximos-passos)

---

## 1. Objetivo da etapa

O objetivo do cenário C3 é avaliar o impacto da adição de uma ferramenta de **Software Composition Analysis (SCA)** ao pipeline CI/CD que já conta com análise SAST. O Trivy é integrado ao pipeline para escanear dependências do projeto e a imagem Docker gerada, registrando o tempo adicional introduzido e as vulnerabilidades identificadas.

A etapa responde, em parte, à pergunta de pesquisa do TCC:

> Como a integração de ferramentas de análise de segurança — SAST, DAST e SCA — afeta o lead time em pipelines CI/CD, e como otimizar esse impacto?

Ao final da etapa, são produzidos dados experimentais que permitem comparar o lead time do C3 com os cenários C1 (baseline) e C2 (SAST), além de um inventário quantitativo das vulnerabilidades detectadas na aplicação e na imagem Docker.

---

## 2. Contexto experimental

O experimento do TCC está organizado em cinco cenários incrementais:

| Cenário | Descrição                             | Status         |
|---------|---------------------------------------|----------------|
| C1      | Pipeline baseline (sem segurança)     | Concluído      |
| C2      | Pipeline baseline + SAST (SonarQube)  | Concluído      |
| C3      | Pipeline C2 + SCA (Trivy)             | **Esta etapa** |
| C4      | Pipeline C3 + DAST                    | Futuro         |
| C5      | Pipeline otimizado                    | Futuro         |

O C3 parte diretamente do C2, acrescentando dois scans do Trivy: um no sistema de arquivos do repositório (dependências) e outro na imagem Docker construída. Todo o restante do pipeline permanece idêntico ao C2 para que a diferença de tempo observada possa ser atribuída exclusivamente à etapa SCA.

---

## 3. Conceitos principais

### 3.1 SAST

**Static Application Security Testing (SAST)** é a análise de segurança realizada sobre o código-fonte, sem executar a aplicação. O SAST identifica padrões problemáticos — como injeção de SQL, uso de funções inseguras ou exposição de credenciais — por meio de regras estáticas aplicadas diretamente ao código.

No contexto deste TCC, o SAST é realizado pelo SonarQube, introduzido no cenário C2 e mantido no C3.

### 3.2 SCA

**Software Composition Analysis (SCA)** é a análise de segurança voltada para os componentes de terceiros utilizados pelo projeto: bibliotecas, pacotes e dependências declaradas em arquivos como `requirements.txt`, `package.json` ou `Pipfile.lock`. O SCA verifica se algum desses componentes possui vulnerabilidades conhecidas, correlacionando-os com bases de dados públicas como o NVD (National Vulnerability Database).

O SCA complementa o SAST porque este último não analisa código de terceiros — apenas o código produzido pelo time. Juntos, cobrem tanto o código interno quanto a cadeia de dependências.

### 3.3 Trivy

**Trivy** é uma ferramenta de segurança open source desenvolvida pela Aqua Security. Ela realiza varreduras em múltiplos alvos: sistemas de arquivos, imagens Docker, repositórios Git, arquivos de configuração de infraestrutura (IaC) e artefatos de containers.

O Trivy foi escolhido para o C3 pelos seguintes motivos:

- Instalação simples, sem dependências complexas.
- Suporte nativo a scan de filesystem e imagem Docker em um único binário.
- Geração de relatórios em múltiplos formatos: JSON, SARIF e texto.
- Integração direta com GitHub Actions via upload de relatórios SARIF para o GitHub Security.
- Amplamente adotado na indústria e com documentação abrangente.

### 3.4 CVE e severidade

**CVE (Common Vulnerabilities and Exposures)** é o sistema de identificação padronizado de vulnerabilidades de segurança. Cada CVE possui um identificador único (ex.: `CVE-2023-12345`) e um score de criticidade calculado pelo sistema **CVSS (Common Vulnerability Scoring System)**.

O Trivy classifica as vulnerabilidades encontradas em quatro níveis de severidade:

| Severidade | Faixa CVSS |
|------------|------------|
| LOW        | 0.1 – 3.9  |
| MEDIUM     | 4.0 – 6.9  |
| HIGH       | 7.0 – 8.9  |
| CRITICAL   | 9.0 – 10.0 |

---

## 4. Escopo do cenário C3

O C3 acrescenta ao pipeline do C2 as seguintes responsabilidades:

- Instalação do Trivy no runner.
- Scan do sistema de arquivos do repositório (`trivy filesystem`) para identificar vulnerabilidades nas dependências declaradas.
- Scan da imagem Docker construída (`trivy image`) para identificar vulnerabilidades nos pacotes do sistema operacional e nas bibliotecas instaladas na imagem.
- Geração de relatórios SARIF para upload ao GitHub Security.
- Medição do tempo total consumido pela etapa SCA.
- Contagem de vulnerabilidades por severidade (LOW, MEDIUM, HIGH, CRITICAL) salva em CSV separado.

> [!IMPORTANT]
> O C3 opera em modo **reportar sem bloquear**. O Trivy é configurado com `exit-code: 0`, o que significa que vulnerabilidades são registradas nos relatórios e nos CSVs, mas não interrompem a execução do pipeline. Esse comportamento é intencional: o objetivo desta etapa é observar e quantificar as vulnerabilidades, não estabelecer políticas de bloqueio.

---

## 5. Arquivos criados ou modificados

| Arquivo                                   | Operação   | Descrição                                                              |
|-------------------------------------------|------------|------------------------------------------------------------------------|
| `.github/workflows/c3-sast-sca.yml`       | Criado     | Workflow principal do C3                                               |
| `ci/config/trivy.yaml`                    | Criado     | Configuração do Trivy para filesystem e image scan                     |
| `analysis/raw/c3_sast_sca.csv`            | Criado     | CSV principal com métricas de tempo por etapa                          |
| `analysis/raw/c3_trivy_summary.csv`       | Criado     | CSV com contagem de vulnerabilidades por severidade e tipo de scan     |
| `ci/scripts/measure_step.sh`              | Modificado | Correção de encoding (remoção de BOM) para execução correta no runner  |
| `docs/07-c3-trivy-sca.md`                 | Criado     | Este documento                                                         |

### Commits relevantes

```text
514ba44 ci: align C3 image tag with Kubernetes manifest
84c1f07 ci: fix measurement script encoding
1732ba3 ci: add C3 SAST and SCA workflow
```

Branch utilizada: `feature/c3-trivy-sca`

---

## 6. Funcionamento do workflow C3

O workflow está definido em [`../.github/workflows/c3-sast-sca.yml`](../.github/workflows/c3-sast-sca.yml) com o nome `C3 - SAST and SCA Pipeline`.

A sequência de execução é a seguinte:

1. **Checkout do repositório** — clona o código na versão do commit que disparou o workflow.
2. **Limpeza de cluster kind anterior** — remove qualquer cluster Kubernetes local residual de execuções anteriores.
3. **Preparação dos arquivos CSV** — cria ou limpa os arquivos de coleta de métricas.
4. **Setup Python** — configura o interpretador Python necessário para a aplicação.
5. **Instalação de dependências** — instala as dependências do projeto.
6. **Testes unitários** — executa a suíte de testes da aplicação.
7. **Análise SAST com SonarQube** — envia o código ao SonarQube para análise estática; o tempo é medido e registrado.
8. **Build da imagem Docker** — constrói a imagem `tcc-devsecops-api:local`; o tempo é medido e registrado.
9. **Instalação do Trivy** — baixa e instala o binário do Trivy no runner.
10. **Marcação do início da etapa SCA** — registra o timestamp de início para cálculo posterior.
11. **Trivy filesystem scan** — escaneia o sistema de arquivos do repositório em busca de vulnerabilidades nas dependências; o tempo é medido individualmente.
12. **Trivy image scan** — escaneia a imagem Docker construída; o tempo é medido individualmente.
13. **Geração de relatórios SARIF** — produz relatórios no formato SARIF para integração com o GitHub Security.
14. **Cálculo do tempo total de SCA** — consolida a duração total da etapa SCA.
15. **Contagem de vulnerabilidades por severidade** — extrai os totais por nível de severidade e salva no CSV de resumo.
16. **Instalação do kind** — prepara o kind (Kubernetes in Docker) para o deploy local.
17. **Criação do cluster Kubernetes local** — sobe um cluster kind para simular o ambiente de produção.
18. **Deploy no Kubernetes** — aplica os manifestos e realiza o deploy da aplicação; o tempo é medido e registrado.
19. **Smoke test** — valida que a aplicação responde corretamente após o deploy; o tempo é medido e registrado.
20. **Registro do tempo total do workflow** — calcula e salva a duração total da execução.
21. **Resumo no GitHub Actions** — gera um step summary com as métricas de tempo e o inventário de vulnerabilidades.
22. **Upload de artifacts** — envia os CSVs e relatórios SARIF como artifacts do workflow.

---

## 7. Configuração do Trivy

A configuração do Trivy está em [`../ci/config/trivy.yaml`](../ci/config/trivy.yaml):

```yaml
timeout: 10m

scan:
  scanners:
    - vuln
  skip-dirs:
    - .git
    - .venv
    - venv
    - __pycache__
    - analysis
    - docs

pkg:
  types:
    - os
    - library

severity:
  - LOW
  - MEDIUM
  - HIGH
  - CRITICAL

vulnerability:
  ignore-unfixed: false

exit-code: 0
```

Explicação de cada bloco:

| Chave                        | Valor                                      | Descrição                                                                                                           |
|------------------------------|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| `timeout`                    | `10m`                                      | Tempo máximo de execução de cada scan. Evita que o pipeline trave indefinidamente em caso de falha de rede ou volume excessivo de dados. |
| `scan.scanners`              | `[vuln]`                                   | Define que apenas a varredura de vulnerabilidades (CVEs) será realizada, excluindo outros scanners como `secret` ou `config`. |
| `scan.skip-dirs`             | `.git`, `.venv`, `venv`, `__pycache__`, `analysis`, `docs` | Diretórios ignorados no scan de filesystem. Evita falsos positivos e reduz o tempo de varredura em diretórios irrelevantes para segurança. |
| `pkg.types`                  | `[os, library]`                            | Tipos de pacotes analisados: pacotes do sistema operacional (ex.: `apt`, `apk`) e bibliotecas de linguagem (ex.: `pip`, `npm`). |
| `severity`                   | `LOW, MEDIUM, HIGH, CRITICAL`              | Todos os níveis de severidade são reportados. Nenhum é filtrado ou ignorado.                                        |
| `vulnerability.ignore-unfixed` | `false`                                  | Vulnerabilidades sem correção disponível também são reportadas. Isso garante visibilidade completa do risco, mesmo quando não há patch. |
| `exit-code`                  | `0`                                        | O Trivy sempre retorna código de saída `0`, independentemente do número ou severidade das vulnerabilidades encontradas. Isso mantém o pipeline em modo **reportar sem bloquear**. |

> [!WARNING]
> Os resultados do Trivy podem variar entre execuções por causa do cache local de base de dados de vulnerabilidades. Quando o banco de dados do Trivy é baixado pela primeira vez ou atualizado, scans subsequentes podem diferir de scans anteriores se novas CVEs forem publicadas no intervalo. Em ambiente self-hosted, o cache Docker e o cache do Trivy também podem influenciar os tempos medidos, especialmente nas primeiras execuções após reinicialização do runner.

---

## 8. Métricas coletadas

### CSV principal — [`../analysis/raw/c3_sast_sca.csv`](../analysis/raw/c3_sast_sca.csv)

O arquivo segue o mesmo esquema adotado nos cenários C1 e C2, preservando a comparabilidade experimental entre cenários:

```csv
scenario,run_id,run_number,commit_sha,step_name,start_timestamp,end_timestamp,duration_seconds,status
```

| Coluna              | Descrição                                                      |
|---------------------|----------------------------------------------------------------|
| `scenario`          | Identificador do cenário (`c3`)                                |
| `run_id`            | ID único da execução no GitHub Actions                         |
| `run_number`        | Número sequencial da execução                                  |
| `commit_sha`        | Hash do commit que disparou o workflow                         |
| `step_name`         | Nome da etapa medida (ex.: `sonarqube_sast`, `sca_total`)      |
| `start_timestamp`   | Timestamp Unix de início da etapa                              |
| `end_timestamp`     | Timestamp Unix de fim da etapa                                 |
| `duration_seconds`  | Duração calculada em segundos                                  |
| `status`            | Resultado da etapa (`success` ou `failure`)                    |

### CSV de resumo de vulnerabilidades — [`../analysis/raw/c3_trivy_summary.csv`](../analysis/raw/c3_trivy_summary.csv)

Este arquivo fica separado do CSV principal porque registra métricas de segurança, não de tempo. Misturá-las no mesmo arquivo dificultaria análises futuras:

```csv
scenario,run_id,run_number,commit_sha,trivy_target,trivy_scan_type,vuln_low,vuln_medium,vuln_high,vuln_critical,total_vulnerabilities
```

| Coluna                  | Descrição                                                            |
|-------------------------|----------------------------------------------------------------------|
| `trivy_target`          | Alvo do scan (`filesystem` ou nome da imagem Docker)                 |
| `trivy_scan_type`       | Tipo de scan (`fs` para filesystem, `image` para imagem Docker)      |
| `vuln_low`              | Contagem de vulnerabilidades de severidade LOW                       |
| `vuln_medium`           | Contagem de vulnerabilidades de severidade MEDIUM                    |
| `vuln_high`             | Contagem de vulnerabilidades de severidade HIGH                      |
| `vuln_critical`         | Contagem de vulnerabilidades de severidade CRITICAL                  |
| `total_vulnerabilities` | Soma total de todas as severidades                                   |

> [!NOTE]
> Valores `0s` (zero segundos) nas colunas `sca_fs` e similares indicam que a duração da etapa foi inferior à granularidade de 1 segundo adotada pelo script de medição, não que a etapa não foi executada. O Trivy filesystem scan foi executado normalmente em todas as amostras.

---

## 9. Resultados das execuções

### Tempos por etapa (em segundos)

| Amostra | SonarQube SAST | Docker Build | SCA FS | SCA Image | SCA Total | Kubernetes Deploy | Smoke Test | Workflow Total |
|---------|----------------|--------------|--------|-----------|-----------|-------------------|------------|----------------|
| 1       | 26             | 3            | 0      | 0         | 1         | 40                | 5          | 116            |
| 2       | 13             | 2            | 0      | 0         | 0         | 29                | 5          | 107            |
| 3       | 33             | 3            | 0      | 1         | 1         | 43                | 5          | 149            |
| 4       | 16             | 6            | 0      | 1         | 1         | 46                | 5          | 132            |
| 5       | 14             | 3            | 0      | 0         | 0         | 37                | 5          | 127            |

### Médias consolidadas (em segundos)

| Etapa              | Média (s) |
|--------------------|-----------|
| SonarQube SAST     | 20,40     |
| Docker Build       | 3,40      |
| SCA Filesystem     | 0,00      |
| SCA Image          | 0,40      |
| **SCA Total**      | **0,60**  |
| Kubernetes Deploy  | 39,00     |
| Smoke Test         | 5,00      |
| **Workflow Total** | **126,20**|

A etapa SCA apresentou impacto médio de **0,60 segundo** no lead time total do pipeline. Esse resultado indica que o Trivy, nas condições experimentais com cache ativo, introduz overhead desprezível em termos absolutos. A maior parte do lead time do C3 continua sendo dominada pelo deploy no Kubernetes (39,00 s) e pela análise SAST (20,40 s).

---

## 10. Vulnerabilidades encontradas

### Resumo por tipo de scan

| Tipo de scan             | LOW | MEDIUM | HIGH | CRITICAL | Total |
|--------------------------|-----|--------|------|----------|-------|
| Filesystem (dependências)| 0   | 1      | 0    | 0        | 1     |
| Imagem Docker            | 63  | 31     | 8    | 2        | 104   |
| **Total geral**          | **63** | **32** | **8** | **2** | **105** |

### Análise dos resultados

O scan de **filesystem** identificou 1 vulnerabilidade de severidade MEDIUM nas dependências declaradas do projeto. O volume reduzido é esperado em projetos com poucas dependências externas ou com dependências recentemente atualizadas.

O scan da **imagem Docker** revelou 104 vulnerabilidades, distribuídas principalmente em pacotes do sistema operacional base da imagem. A concentração em LOW e MEDIUM indica que as vulnerabilidades de maior impacto existem, mas em quantidade controlada (8 HIGH e 2 CRITICAL). Vulnerabilidades em imagens Docker são comuns quando se utiliza imagens base sem aplicar hardening ou sem escolher variantes slim ou distroless.

As vulnerabilidades CRITICAL e HIGH identificadas devem ser investigadas em etapa futura (C5 — pipeline otimizado), onde estratégias de mitigação poderão ser avaliadas sem prejudicar a comparabilidade dos cenários C1 a C4.

---

## 11. Problemas encontrados e correções

### Problema 1 — Falha inicial no SonarQube SAST

**Sintoma:** a etapa de análise SAST falhou nas primeiras tentativas de execução do workflow C3.

**Possível causa:** o container do SonarQube estava ainda inicializando quando o workflow tentou se conectar, ou a `SONAR_HOST_URL` configurada apontava para um endereço inacessível dentro da rede Docker.

**Diagnóstico:** o container `tcc-sonarqube` foi verificado e validado como `UP` via `docker ps`. A URL foi corrigida para o endereço acessível dentro da rede Docker utilizada pelo runner self-hosted.

**Correção:** ajuste da variável `SONAR_HOST_URL` para o endereço correto, garantindo que o SonarQube Scanner conseguisse se comunicar com o servidor durante a execução do workflow.

### Problema 2 — Erro de encoding no `measure_step.sh`

**Sintoma:**

```text
./ci/scripts/measure_step.sh: line 1: ﻿#!/usr/bin/env: No such file or directory
```

**Causa:** o arquivo `ci/scripts/measure_step.sh` foi salvo com **BOM (Byte Order Mark)** no início do arquivo, caractere invisível que corrompeu a linha do shebang (`#!/usr/bin/env bash`) e impediu sua interpretação correta pelo shell.

**Correção:** o arquivo foi re-salvo sem BOM, utilizando encoding UTF-8 puro. O commit `84c1f07` registra essa correção.

### Problema 3 — Timeout no deploy Kubernetes

**Sintoma:** o deploy no Kubernetes travava aguardando a imagem Docker que nunca era encontrada no cluster kind.

**Causa:** a imagem Docker estava sendo construída com uma tag diferente da referenciada no manifesto Kubernetes. O workflow usava uma tag e o manifesto esperava outra.

**Correção:** o `IMAGE_NAME` foi padronizado para `tcc-devsecops-api:local` tanto no step de build quanto nos manifestos Kubernetes. O commit `514ba44` registra esse alinhamento.

---



## 13. Limitações metodológicas

- **Cache do Trivy:** o banco de dados de vulnerabilidades do Trivy é armazenado em cache local. Execuções com cache aquecido tendem a ser mais rápidas do que a primeira execução, que realiza o download completo. Os tempos medidos no C3 refletem execuções com cache ativo, o que pode subestimar o overhead real em ambientes sem cache.

- **Cache Docker:** a imagem Docker base já estava presente no runner self-hosted em todas as amostras, reduzindo o tempo de build. Em um runner limpo (como os hospedados pelo GitHub), o tempo de `docker_build` seria maior.

- **Ambiente self-hosted:** o runner utilizado é uma máquina local compartilhada. Variações de carga do sistema operacional, memória disponível e estado do cluster kind podem influenciar os tempos medidos, especialmente na etapa de deploy Kubernetes.

- **Granularidade de 1 segundo:** o script `measure_step.sh` mede duração em segundos inteiros. Etapas com duração inferior a 1 segundo são registradas como `0s`. Isso explica os valores nulos em `sca_fs` em quatro das cinco amostras.

- **Modo sem bloqueio:** como o Trivy está configurado com `exit-code: 0`, vulnerabilidades CRITICAL e HIGH não interrompem o pipeline. Isso é adequado para a fase de observação, mas não representa uma política de segurança adequada para ambientes de produção.

- **Amostra de cinco execuções:** o número de amostras é limitado pela natureza experimental do TCC. Análises estatísticas mais robustas exigiriam amostras maiores.

---


*Documentação gerada para o TCC: "Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD"*
