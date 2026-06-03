# 🔐 Etapa 6 — Pipeline C2: Análise SAST com SonarQube

> **TCC:** Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD
> **Cenário:** C2 — Pipeline baseline com adição de análise SAST via SonarQube Community
> **Branch:** `feature/c2-sonarqube-sast`
> **Repositório:** [r2WillDev/tcc-devsecops-pipeline](https://github.com/r2WillDev/tcc-devsecops-pipeline)

---

## 📋 Sumário

1. [Objetivo do Cenário C2](#objetivo-do-cenário-c2)
2. [Arquivos criados ou alterados](#arquivos-criados-ou-alterados)
3. [Infraestrutura local do SonarQube](#infraestrutura-local-do-sonarqube)
4. [Secrets configurados no GitHub](#secrets-configurados-no-github)
5. [Configuração do SonarScanner](#configuração-do-sonarscanner)
6. [CSV de coleta do C2](#csv-de-coleta-do-c2)
7. [Workflow C2](#workflow-c2)
8. [Decisão: self-hosted runner](#decisão-self-hosted-runner)
9. [Problemas encontrados e ajustes realizados](#problemas-encontrados-e-ajustes-realizados)
10. [Validação técnica do C2](#validação-técnica-do-c2)
11. [Evidências coletadas](#evidências-coletadas)
12. [Próximos passos](#próximos-passos)

---

## 🎯 Objetivo do Cenário C2

O cenário C2 representa o segundo nível da cadeia experimental do TCC. A lógica de composição é:

```
C2 = C1 (baseline) + análise SAST com SonarQube
```

O objetivo é **medir o impacto isolado da ferramenta de análise estática de segurança (SAST)** sobre o lead time total do pipeline, sem introduzir outras variáveis.

Para garantir a comparabilidade dos resultados, o pipeline C2 mantém a estrutura integral do C1, adicionando exclusivamente a etapa `sonarqube_sast`. Todas as demais etapas — testes unitários, build da imagem Docker, criação do cluster Kubernetes, deploy e smoke test — permanecem com a mesma lógica de execução e medição.

Esse isolamento metodológico é fundamental para que a diferença de tempo observada entre C1 e C2 possa ser atribuída com razoável confiança à adição da análise SAST.

---

## 📁 Arquivos criados ou alterados

| Arquivo | Tipo | Descrição |
|---|---|---|
| `infra/sonarqube/docker-compose.yml` | Infraestrutura | Define o ambiente local do SonarQube via Docker Compose |
| `ci/config/sonar-project.properties` | Configuração | Parâmetros da análise SAST para o SonarScanner CLI |
| `analysis/raw/c2_sast.csv` | Dados | Cabeçalho base do CSV de coleta de resultados do C2 |
| `.github/workflows/c2-sast.yml` | CI/CD | Workflow principal do cenário C2 no GitHub Actions |
| `docs/06-c2-sonarqube-sast.md` | Documentação | Este arquivo |

---

## 🐳 Infraestrutura local do SonarQube

### Arquivo: `infra/sonarqube/docker-compose.yml`

Foi criado um ambiente local do SonarQube utilizando Docker Compose. Essa abordagem foi adotada porque o SonarQube Community Edition não oferece serviço hospedado gratuito adequado para integração com self-hosted runners, e o ambiente local permite controle total sobre o servidor de análise durante os experimentos.

O serviço foi exposto na porta padrão `9000`, tornando a interface web acessível em:

```
http://localhost:9000
```

Após subir o ambiente com `docker compose up -d`, foi realizada a configuração inicial do SonarQube:

- **Project key:** `tcc-devsecops-pipeline`
- **Project name:** `TCC DevSecOps Pipeline`
- **Modo de análise:** CI-based (token gerado manualmente)

O token de análise gerado foi configurado como secret no repositório GitHub, conforme descrito na seção seguinte. Nenhum valor sensível é armazenado diretamente no código-fonte do projeto.

> ⚠️ **Segurança:** O arquivo `docker-compose.yml` não contém senhas, tokens ou credenciais hardcoded. Todos os valores sensíveis são injetados via variáveis de ambiente ou secrets do GitHub Actions.

---

## 🔐 Secrets configurados no GitHub

Para que o workflow C2 pudesse se autenticar e enviar os resultados da análise ao SonarQube local, foram configurados dois secrets no repositório do GitHub:

| Secret | Finalidade |
|---|---|
| `SONAR_TOKEN` | Token de autenticação para envio da análise ao SonarQube |
| `SONAR_HOST_URL` | URL usada pelo SonarScanner para acessar o servidor SonarQube |

### Por que `SONAR_HOST_URL` não é `http://localhost:9000`?

O valor configurado para `SONAR_HOST_URL` foi:

```
http://tcc-sonarqube:9000
```

Essa configuração é necessária porque o SonarScanner é executado **dentro de um container Docker**, e dentro desse contexto o endereço `localhost` referencia o próprio container do scanner, não o host ou o container do SonarQube.

A comunicação correta entre containers Docker é feita pelo **nome do serviço definido na rede Docker**. O container do SonarQube pertence à rede `sonarqube_default` e seu nome de serviço é `tcc-sonarqube`. Por isso, o scanner precisa acessar o SonarQube pelo endereço `http://tcc-sonarqube:9000`, e o workflow foi ajustado para conectar o container do scanner à mesma rede Docker do SonarQube:

```bash
--network "$SONARQUBE_NETWORK"
```

---

## ⚙️ Configuração do SonarScanner

### Arquivo: `ci/config/sonar-project.properties`

```properties
sonar.projectKey=tcc-devsecops-pipeline
sonar.projectName=TCC DevSecOps Pipeline
sonar.projectVersion=1.0

sonar.sources=app
sonar.tests=app
sonar.test.inclusions=app/test_*.py
sonar.exclusions=app/test_*.py,**/__pycache__/**,**/.pytest_cache/**,**/.venv/**,**/venv/**,**/.mypy_cache/**,**/.ruff_cache/**

sonar.sourceEncoding=UTF-8
sonar.python.version=3.12
```

### Explicação das propriedades principais

| Propriedade | Valor | Explicação |
|---|---|---|
| `sonar.projectKey` | `tcc-devsecops-pipeline` | Identificador único do projeto no SonarQube |
| `sonar.sources` | `app` | Diretório raiz do código-fonte da aplicação FastAPI |
| `sonar.tests` | `app` | Diretório onde os arquivos de teste estão localizados |
| `sonar.test.inclusions` | `app/test_*.py` | Padrão de inclusão dos arquivos de teste |
| `sonar.exclusions` | `app/test_*.py, caches, venvs` | Exclusão de arquivos de teste e diretórios auxiliares da análise de código-fonte |
| `sonar.python.version` | `3.12` | Informa ao analisador a versão do Python utilizada, evitando falsos positivos por incompatibilidade de sintaxe |

A separação explícita entre `sonar.sources` e a exclusão dos arquivos de teste via `sonar.exclusions` garante que o SonarQube analise apenas o código de produção, mantendo as métricas de qualidade e segurança coerentes. Os arquivos de teste são referenciados separadamente via `sonar.test.inclusions` para que as métricas de cobertura sejam computadas corretamente.

---

## 📊 CSV de coleta do C2

### Arquivo: `analysis/raw/c2_sast.csv`

```csv
scenario,run_id,run_number,commit_sha,step_name,start_timestamp,end_timestamp,duration_seconds,status
```

Este arquivo define o **esquema de coleta de dados** do cenário C2. Ele não contém linhas de dados — sua função é documentar e versionar o cabeçalho esperado para os arquivos de execução.

Durante cada execução do workflow, o GitHub Actions gera o arquivo de execução correspondente:

```
analysis/raw/c2_sast_run.csv
```

Esse arquivo temporário é preenchido passo a passo à medida que cada etapa medida é concluída, e ao final do workflow é enviado como artifact do GitHub Actions, permitindo rastreabilidade por `run_id` e `commit_sha`.

A convenção de nomenclatura adotada para as execuções oficiais é:

```
c2_sast_run_01.csv
c2_sast_run_02.csv
...
c2_sast_run_05.csv
```

---

## 🚀 Workflow C2

### Arquivo: `.github/workflows/c2-sast.yml`

#### Variáveis de ambiente

```yaml
env:
  SCENARIO: C2-sast
  RESULTS_FILE: analysis/raw/c2_sast_run.csv
  IMAGE_NAME: tcc-devsecops-api:local
  CLUSTER_NAME: tcc-devsecops
  SONAR_PROJECT_SETTINGS: ci/config/sonar-project.properties
```

#### Etapas do workflow

O pipeline C2 foi estruturado para seguir o mesmo fluxo do C1, com a adição da etapa de análise SAST posicionada logo após os testes unitários — antes do build da imagem Docker. Essa posição foi escolhida porque a análise estática incide sobre o código-fonte, não sobre o artefato compilado.

| # | Etapa | Descrição |
|---|---|---|
| 1 | `Checkout repository` | Clona o repositório na versão do commit acionador |
| 2 | `Cleanup previous kind cluster container` | Remove container kind de execuções anteriores (fora da medição) |
| 3 | `Prepare results CSV` | Cria o arquivo CSV com o cabeçalho e define o início da medição |
| 4 | `Set up Python` | Configura o Python 3.12 no ambiente do runner |
| 5 | `Make measure script executable` | Concede permissão de execução ao script `measure_step.sh` |
| 6 | `Install dependencies` | Instala as dependências da aplicação FastAPI (medido) |
| 7 | `Run unit tests` | Executa os testes unitários com pytest (medido) |
| 8 | `Run SonarQube SAST analysis` | Executa a análise SAST via SonarScanner CLI (medido — etapa nova no C2) |
| 9 | `Build Docker image` | Constrói a imagem Docker da aplicação (medido) |
| 10 | `Install kind` | Instala o `kind` em `$HOME/.local/bin` |
| 11 | `Create kind cluster` | Cria o cluster Kubernetes local (medido como parte do deploy) |
| 12 | `Deploy to Kubernetes` | Aplica os manifests e aguarda o rollout (medido) |
| 13 | `Kubernetes smoke test` | Verifica disponibilidade da aplicação via `curl` (medido) |
| 14 | `Record workflow total duration` | Registra o tempo total do pipeline no CSV |
| 15 | `Display metrics` | Exibe o CSV de resultados no log do workflow |
| 16 | `Write job summary` | Escreve o resumo do run no GitHub Actions Summary |
| 17 | `Upload CSV artifact` | Envia o CSV como artifact para download |

#### Posicionamento da etapa de SAST

A etapa `sonarqube_sast` foi inserida entre `unit_tests` e `docker_build`. Essa sequência é tecnicamente coerente: a análise estática deve ocorrer sobre o código-fonte antes que ele seja empacotado em imagem, refletindo um pipeline DevSecOps com "shift-left" de segurança.

---

## 🖥️ Decisão: self-hosted runner

### Contexto

O pipeline C1 utilizava um GitHub-hosted runner:

```yaml
runs-on: ubuntu-latest
```

Para o C2, foi necessário migrar para um self-hosted runner:

```yaml
runs-on: self-hosted
```

### Motivo técnico

O SonarQube foi executado localmente na máquina de desenvolvimento, dentro de um container Docker gerenciado pelo Docker Desktop. Um GitHub-hosted runner, por ser uma máquina virtual efêmera hospedada remotamente, **não tem acesso à rede local do usuário** e, portanto, não consegue se comunicar com serviços expostos em `localhost` ou em redes Docker locais.

A solução adotada foi configurar um self-hosted runner no ambiente local, diretamente via WSL 2 com Ubuntu 24.04, onde o Docker Desktop e o SonarQube estão acessíveis.

### Ambiente do runner

| Item | Valor |
|---|---|
| Sistema operacional | Ubuntu 24.04.4 LTS |
| Plataforma de execução | WSL 2 (Windows Subsystem for Linux) |
| Docker | Docker Desktop com integração WSL habilitada |
| Runner | GitHub Actions self-hosted runner |
| SonarQube | Container Docker local (rede `sonarqube_default`) |

### ⚠️ Limitação metodológica

A mudança do tipo de runner entre C1 e C2 representa uma diferença no ambiente de execução, o que deve ser reconhecida como **limitação metodológica** do experimento.

Para que a comparação entre C1 e C2 seja estritamente controlada, o ideal seria executar ambos os cenários no mesmo tipo de runner. Reconhece-se que a adoção do self-hosted runner introduz variáveis ambientais distintas — como desempenho de hardware local, latência de rede e overhead do Docker Desktop — que podem influenciar os tempos medidos.

Essa limitação será discutida na seção de análise dos resultados do TCC, com os devidos cuidados interpretativos.

---

## 🛠️ Problemas encontrados e ajustes realizados

Durante a implementação do cenário C2, foram identificados e solucionados cinco problemas. Cada um é documentado abaixo com o contexto, o erro observado e a solução adotada.

---

### Problema 1 — Dependência `libicu` ausente no Ubuntu 26.04

**Contexto:** A primeira tentativa de configurar o self-hosted runner foi realizada em uma instância do Ubuntu 26.04 no WSL 2.

**Erro:**
```
Libicu's dependencies is missing for Dotnet Core 6.0
```

**Causa:** O Ubuntu 26.04 possui uma versão de `libicu` incompatível com as dependências esperadas por componentes internos do runner do GitHub Actions.

**Solução:** O ambiente foi recriado utilizando **Ubuntu 24.04 LTS**, que possui a versão compatível da biblioteca. Após a reinstalação do runner nessa versão, o problema não ocorreu.

---

### Problema 2 — Docker não disponível no WSL 2

**Contexto:** Após configurar o Ubuntu 24.04 no WSL 2, o comando `docker` não estava disponível na sessão do runner.

**Erro:**
```
The command 'docker' could not be found in this WSL 2 distro.
```

**Causa:** O Docker Desktop não estava integrado à distribuição Ubuntu do WSL 2.

**Solução:** A integração foi habilitada pelo painel do Docker Desktop:

```
Docker Desktop > Settings > Resources > WSL Integration > Enable for Ubuntu
```

Após reiniciar a sessão WSL, os comandos `docker version`, `docker ps` e `docker compose version` passaram a funcionar corretamente no ambiente do runner.

---

### Problema 3 — SonarScanner não conseguia acessar o SonarQube

**Contexto:** O SonarQube estava em execução e acessível via navegador em `http://localhost:9000`. No entanto, ao executar o SonarScanner dentro de um container Docker, a análise falhava ao tentar se conectar ao servidor.

**Causa:** Dentro de um container Docker, o endereço `localhost` referencia o próprio container — não o host nem os outros containers. O SonarScanner, executado em um container isolado, não conseguia alcançar o SonarQube por esse endereço.

**Solução:**

1. Identificar a rede Docker à qual o SonarQube pertence:
   ```
   sonarqube_default
   ```

2. Verificar o nome do serviço SonarQube na rede:
   ```
   tcc-sonarqube
   ```

3. Testar a conectividade entre containers usando o nome do serviço:
   ```
   http://tcc-sonarqube:9000
   ```

4. Atualizar o secret `SONAR_HOST_URL` para:
   ```
   http://tcc-sonarqube:9000
   ```

5. Ajustar o workflow para conectar o container do SonarScanner à mesma rede Docker:
   ```bash
   --network "$SONARQUBE_NETWORK"
   ```

---

### Problema 4 — Instalação do `kind` solicitava senha (sudo)

**Contexto:** A etapa de instalação do `kind` utilizava `sudo` para mover o binário para `/usr/local/bin`.

**Problema:** No ambiente do self-hosted runner sem TTY interativo, o `sudo` aguardava entrada de senha, causando timeout na etapa e potencialmente interferindo na medição do lead time.

**Solução:**

- Remover o uso de `sudo` da etapa de instalação.
- Instalar o binário do `kind` em um diretório com permissão de escrita pelo usuário:
  ```
  $HOME/.local/bin
  ```
- Adicionar esse diretório ao `GITHUB_PATH` para que o `kind` seja encontrado nas etapas subsequentes:
  ```bash
  echo "$HOME/.local/bin" >> "$GITHUB_PATH"
  ```

---

### Problema 5 — Cluster `kind` anterior causando falha na criação

**Contexto:** Em execuções consecutivas do workflow sem limpeza prévia do ambiente, a etapa de criação do cluster falhou.

**Erro:**
```
ERROR: failed to create cluster: node(s) already exist for a cluster with the name "tcc-devsecops"
```

**Causa:** O container Docker do nó do cluster `kind` da execução anterior permanecia ativo, impedindo a criação de um novo cluster com o mesmo nome.

**Solução:** Adição de uma etapa de limpeza explícita **antes** do início da medição do pipeline:

```yaml
- name: Cleanup previous kind cluster container
  run: |
    docker rm -f "${CLUSTER_NAME}-control-plane" 2>/dev/null || true
```

> **Decisão de posicionamento:** Essa etapa foi inserida **antes** do passo `Prepare results CSV`, que marca o início da janela de medição. Dessa forma, o tempo de limpeza do ambiente não é contabilizado no lead time do pipeline, garantindo que a medição reflita apenas a execução do pipeline em si.

---

## ✅ Validação técnica do C2

Após a resolução de todos os problemas documentados na seção anterior, foi realizado um run de validação para confirmar que o workflow C2 executa de ponta a ponta sem erros.

### Resultado da validação

| Item | Resultado |
|---|---|
| Status do workflow | ✅ Sucesso |
| Todas as etapas concluídas | ✅ Sim |
| Pedido de senha durante execução | ✅ Não |
| Artifact disponível para download | ✅ Sim |
| GitHub Actions Summary com CSV | ✅ Sim |
| SonarQube acessível durante análise | ✅ Sim |
| Quality Gate disponível no SonarQube | ✅ Sim |

### Identificação do run de validação

```
run_id:     26893629530
run_number: 3
commit_sha: 2d200ff6537e1fa9f33878acdf5e4afc2cf0d174
```

### CSV coletado no run de validação

```csv
scenario,run_id,run_number,commit_sha,step_name,start_timestamp,end_timestamp,duration_seconds,status
C2-sast,26893629530,3,2d200ff6537e1fa9f33878acdf5e4afc2cf0d174,install_dependencies,2026-06-03T15:04:29Z,2026-06-03T15:04:29Z,0,success
C2-sast,26893629530,3,2d200ff6537e1fa9f33878acdf5e4afc2cf0d174,unit_tests,2026-06-03T15:04:30Z,2026-06-03T15:04:31Z,1,success
C2-sast,26893629530,3,2d200ff6537e1fa9f33878acdf5e4afc2cf0d174,sonarqube_sast,2026-06-03T15:04:31Z,2026-06-03T15:04:46Z,15,success
C2-sast,26893629530,3,2d200ff6537e1fa9f33878acdf5e4afc2cf0d174,docker_build,2026-06-03T15:04:46Z,2026-06-03T15:04:49Z,3,success
C2-sast,26893629530,3,2d200ff6537e1fa9f33878acdf5e4afc2cf0d174,kubernetes_deploy,2026-06-03T15:05:19Z,2026-06-03T15:05:58Z,39,success
C2-sast,26893629530,3,2d200ff6537e1fa9f33878acdf5e4afc2cf0d174,kubernetes_smoke_test,2026-06-03T15:05:58Z,2026-06-03T15:06:03Z,5,success
C2-sast,26893629530,3,2d200ff6537e1fa9f33878acdf5e4afc2cf0d174,workflow_total,2026-06-03T15:04:29Z,2026-06-03T15:06:03Z,94,success
```

### Tempos por etapa (run de validação)

| Etapa | Duração |
|---|---|
| `install_dependencies` | 0 s |
| `unit_tests` | 1 s |
| `sonarqube_sast` | **15 s** |
| `docker_build` | 3 s |
| `kubernetes_deploy` | 39 s |
| `kubernetes_smoke_test` | 5 s |
| **`workflow_total`** | **94 s** |

> **Observação:** Este run foi realizado durante o processo de ajuste do ambiente e do workflow. Por isso, é classificado como **validação técnica**, não como amostra experimental oficial. Os dados coletados neste run **não serão utilizados** na análise comparativa do TCC. As 5 execuções oficiais serão realizadas em condições estabilizadas, conforme descrito na seção de próximos passos.

---

## 📸 Evidências coletadas

As evidências abaixo devem ser capturadas e armazenadas no diretório `docs/assets/` para compor o registro desta etapa.

| # | Evidência | Nome sugerido |
|---|---|---|
| 1 | Interface do SonarQube em execução local (`http://localhost:9000`) | `06-c2-sonarqube-running-local.png` |
| 2 | Projeto criado no SonarQube (`tcc-devsecops-pipeline`) | `07-c2-sonarqube-project.png` |
| 3 | Secrets configurados no GitHub (sem exibir valores) | `06-c2-github-secrets.png` |
| 4 | Self-hosted runner com status `Idle` (online e aguardando) | `10-self-hosted-runner-idle-after-success.png` |
| 5 | Workflow C2 finalizado com sucesso no GitHub Actions | `06-c2-workflow-success.png` |
| 6 | GitHub Actions Summary exibindo o CSV de resultados | `07-c2-summary-csv.png` |
| 7 | Artifact disponível para download na página do run | `08-c2-artifact-available.png` |
| 8 | Quality Gate no SonarQube após análise do C2 | `09-sonarqube-analysis-after-c2-run.png` |
| 9 | Log da etapa `Run SonarQube SAST analysis` | `11-c2-run-logs-sonarqube-sast.png` |
| 10 | Log da etapa `Deploy to Kubernetes` | `12-c2-run-logs-kubernetes-deploy.png` |
| 11 | CSV artifact baixado da execução de validação | `c2_sast_run_validation.csv` |

---

## 🔭 Próximos passos

Com a validação técnica do cenário C2 concluída, a infraestrutura e o workflow estão prontos para a coleta dos dados experimentais oficiais.

### Execuções oficiais planejadas

Serão realizadas **5 execuções independentes** do workflow C2, cada uma gerando um arquivo CSV de resultados:

```
analysis/raw/c2_sast_run_01.csv
analysis/raw/c2_sast_run_02.csv
analysis/raw/c2_sast_run_03.csv
analysis/raw/c2_sast_run_04.csv
analysis/raw/c2_sast_run_05.csv
```

Cada execução deve ocorrer com o ambiente estabilizado (SonarQube em execução, runner idle, sem processos concorrentes significativos) para minimizar ruídos nas medições.

### Comparação com o C1

Após a coleta das 5 amostras oficiais do C2, os resultados serão comparados com as execuções equivalentes do cenário C1 (baseline), com foco nas seguintes métricas:

| Métrica | Objetivo da análise |
|---|---|
| `sonarqube_sast` | Custo isolado da etapa de SAST no lead time |
| `workflow_total` | Impacto total do C2 sobre o tempo de deploy |
| Δ (C2 − C1) | Incremento de tempo introduzido pela análise SAST |

Os resultados consolidados serão documentados na etapa de análise quantitativa do TCC.

---

*Documentação gerada para o TCC: "Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD"*