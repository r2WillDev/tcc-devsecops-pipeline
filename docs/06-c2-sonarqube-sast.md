# 🔐 Etapa 6 — Pipeline C2: Análise SAST com SonarQube

> **TCC:** Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD  
> **Cenário:** C2 — Pipeline baseline com adição de análise SAST via SonarQube Community  
> **Branch:** `feature/c2-sonarqube-sast`  
> **Repositório:** [r2WillDev/tcc-devsecops-pipeline](https://github.com/r2WillDev/tcc-devsecops-pipeline)

---

## 📋 Sumário

1. [Objetivo do Cenário C2](#objetivo-do-cenario-c2)
2. [Arquivos criados ou alterados](#arquivos-criados-ou-alterados)
3. [Infraestrutura local do SonarQube](#infraestrutura-local-do-sonarqube)
4. [Secrets configurados no GitHub](#secrets-configurados-no-github)
5. [Configuração do SonarScanner](#configuracao-do-sonarscanner)
6. [CSV de coleta dos cenários C2 e C1 self-hosted](#csv-de-coleta-dos-cenarios-c2-e-c1-self-hosted)
7. [Workflow C2](#workflow-c2)
8. [Decisão: self-hosted runner](#decisao-self-hosted-runner)
9. [Controle experimental: comparação entre C1 self-hosted e C2 self-hosted](#controle-experimental-comparacao-entre-c1-self-hosted-e-c2-self-hosted)
10. [Problemas encontrados e ajustes realizados](#problemas-encontrados-e-ajustes-realizados)
11. [Validação técnica dos cenários self-hosted](#validacao-tecnica-dos-cenarios-self-hosted)
12. [Evidências coletadas](#evidencias-coletadas)
13. [Próximos passos](#proximos-passos)

---

<a id="objetivo-do-cenario-c2"></a>
## 🎯 Objetivo do Cenário C2

O cenário C2 representa o segundo nível da cadeia experimental do TCC. A lógica de composição originalmente prevista é:

```text
C2 = C1 (baseline) + análise SAST com SonarQube
```

O objetivo é **medir o impacto isolado da ferramenta de análise estática de segurança (SAST)** sobre o lead time total do pipeline, sem introduzir outras variáveis além da etapa de segurança analisada.

Para garantir a comparabilidade dos resultados, o pipeline C2 mantém a estrutura integral do pipeline baseline, adicionando exclusivamente a etapa `sonarqube_sast`. Todas as demais etapas — instalação de dependências, testes unitários, build da imagem Docker, criação do cluster Kubernetes, deploy e smoke test — permanecem com a mesma lógica de execução e medição.

Esse isolamento metodológico é fundamental para que a diferença de tempo observada entre o baseline e o C2 possa ser atribuída com razoável confiança à adição da análise SAST.

Durante a validação técnica da Etapa 6, foi identificada uma questão metodológica importante: o C1 original havia sido executado em `ubuntu-latest`, enquanto o C2 passou a exigir um `self-hosted runner` local para permitir comunicação com o SonarQube executado no ambiente Docker local. Por isso, dentro desta mesma Etapa 6, foi criada uma variação controlada do baseline chamada **C1 self-hosted**, permitindo comparar:

```text
C1 self-hosted = pipeline baseline sem SAST, executado no mesmo self-hosted runner do C2
C2 self-hosted = mesmo pipeline baseline, adicionando a etapa sonarqube_sast
```

Dessa forma, o objetivo da Etapa 6 passa a incluir não apenas a implementação e validação do C2 com SonarQube, mas também a preparação de um baseline equivalente no mesmo ambiente de execução, fortalecendo a validade interna do experimento.

---

<a id="arquivos-criados-ou-alterados"></a>
## 📁 Arquivos criados ou alterados

| Arquivo | Tipo | Descrição |
|---|---|---|
| `infra/sonarqube/docker-compose.yml` | Infraestrutura | Define o ambiente local do SonarQube via Docker Compose |
| `ci/config/sonar-project.properties` | Configuração | Parâmetros da análise SAST para o SonarScanner CLI |
| `analysis/raw/c2_sast.csv` | Dados | Cabeçalho base do CSV de coleta de resultados do C2 |
| `analysis/raw/c1_self_hosted.csv` | Dados | Cabeçalho base do CSV de coleta de resultados do C1 baseline executado em self-hosted runner |
| `.github/workflows/c2-sast.yml` | CI/CD | Workflow principal do cenário C2 no GitHub Actions |
| `.github/workflows/c1-baseline-self-hosted.yml` | CI/CD | Workflow baseline C1 executado no mesmo self-hosted runner utilizado pelo C2 |
| `docs/06-c2-sonarqube-sast.md` | Documentação | Documento técnico-acadêmico da Etapa 6 |

A inclusão dos arquivos `c1-baseline-self-hosted.yml` e `c1_self_hosted.csv` não representa uma nova etapa do projeto. Esses arquivos foram adicionados como parte do controle metodológico da **Etapa 6**, para permitir uma comparação mais justa entre o pipeline baseline e o pipeline com SAST dentro do mesmo ambiente de execução.

---

<a id="infraestrutura-local-do-sonarqube"></a>
## 🐳 Infraestrutura local do SonarQube

### Arquivo: `infra/sonarqube/docker-compose.yml`

Foi criado um ambiente local do SonarQube utilizando Docker Compose. Essa abordagem foi adotada porque o SonarQube Community Edition não oferece serviço hospedado gratuito adequado para integração com self-hosted runners, e o ambiente local permite controle total sobre o servidor de análise durante os experimentos.

O serviço foi exposto na porta padrão `9000`, tornando a interface web acessível em:

```text
http://localhost:9000
```

Após subir o ambiente com `docker compose up -d`, foi realizada a configuração inicial do SonarQube:

- **Project key:** `tcc-devsecops-pipeline`
- **Project name:** `TCC DevSecOps Pipeline`
- **Modo de análise:** CI-based, com token gerado manualmente

O token de análise gerado foi configurado como secret no repositório GitHub, conforme descrito na seção seguinte. Nenhum valor sensível é armazenado diretamente no código-fonte do projeto.

> [!IMPORTANT]
> **Segurança:** O arquivo `docker-compose.yml` não contém senhas, tokens ou credenciais hardcoded. Todos os valores sensíveis são injetados via variáveis de ambiente ou secrets do GitHub Actions.

---

<a id="secrets-configurados-no-github"></a>
## 🔐 Secrets configurados no GitHub

Para que o workflow C2 pudesse se autenticar e enviar os resultados da análise ao SonarQube local, foram configurados dois secrets no repositório do GitHub:

| Secret | Finalidade |
|---|---|
| `SONAR_TOKEN` | Token de autenticação para envio da análise ao SonarQube |
| `SONAR_HOST_URL` | URL usada pelo SonarScanner para acessar o servidor SonarQube |

### Por que `SONAR_HOST_URL` não é `http://localhost:9000`?

O valor configurado para `SONAR_HOST_URL` foi:

```text
http://tcc-sonarqube:9000
```

Essa configuração é necessária porque o SonarScanner é executado **dentro de um container Docker**, e dentro desse contexto o endereço `localhost` referencia o próprio container do scanner, não o host ou o container do SonarQube.

A comunicação correta entre containers Docker é feita pelo **nome do serviço definido na rede Docker**. O container do SonarQube pertence à rede `sonarqube_default` e seu nome de serviço é `tcc-sonarqube`. Por isso, o scanner precisa acessar o SonarQube pelo endereço `http://tcc-sonarqube:9000`, e o workflow foi ajustado para conectar o container do scanner à mesma rede Docker do SonarQube:

```bash
--network "$SONARQUBE_NETWORK"
```

---

<a id="configuracao-do-sonarscanner"></a>
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

<a id="csv-de-coleta-dos-cenarios-c2-e-c1-self-hosted"></a>
## 📊 CSV de coleta dos cenários C2 e C1 self-hosted

A Etapa 6 utiliza arquivos CSV para padronizar a coleta de métricas temporais dos workflows. O objetivo desses arquivos é registrar, para cada execução, o cenário, o identificador do run, o commit analisado, o nome da etapa medida, os timestamps de início e fim, a duração em segundos e o status da etapa.

### CSV base do C2

#### Arquivo: `analysis/raw/c2_sast.csv`

```csv
scenario,run_id,run_number,commit_sha,step_name,start_timestamp,end_timestamp,duration_seconds,status
```

Este arquivo define o **esquema de coleta de dados** do cenário C2. Ele não contém linhas de dados — sua função é documentar e versionar o cabeçalho esperado para os arquivos de execução.

Durante cada execução do workflow C2, o GitHub Actions gera o arquivo de execução correspondente:

```text
analysis/raw/c2_sast_run.csv
```

Esse arquivo temporário é preenchido passo a passo à medida que cada etapa medida é concluída, e ao final do workflow é enviado como artifact do GitHub Actions, permitindo rastreabilidade por `run_id` e `commit_sha`.

A convenção de nomenclatura adotada para as execuções oficiais do C2 é:

```text
c2_sast_run_01.csv
c2_sast_run_02.csv
c2_sast_run_03.csv
c2_sast_run_04.csv
c2_sast_run_05.csv
```

### CSV base do C1 self-hosted

#### Arquivo: `analysis/raw/c1_self_hosted.csv`

```csv
scenario,run_id,run_number,commit_sha,step_name,start_timestamp,end_timestamp,duration_seconds,status
```

Este arquivo define o mesmo esquema de coleta utilizado no C2, mas aplicado ao baseline C1 executado em self-hosted runner. A padronização do cabeçalho permite comparar os dois cenários com a mesma estrutura de dados.

Durante cada execução do workflow C1 self-hosted, o GitHub Actions gera o arquivo de execução:

```text
analysis/raw/c1_self_hosted_run.csv
```

O artifact gerado pelo GitHub Actions para esse workflow é:

```text
c1-self-hosted-metrics
```

A convenção de nomenclatura adotada para as execuções oficiais do C1 self-hosted é:

```text
c1_self_hosted_run_01.csv
c1_self_hosted_run_02.csv
c1_self_hosted_run_03.csv
c1_self_hosted_run_04.csv
c1_self_hosted_run_05.csv
```

---

<a id="workflow-c2"></a>
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
| 2 | `Cleanup previous kind cluster container` | Remove container kind de execuções anteriores, fora da medição |
| 3 | `Prepare results CSV` | Cria o arquivo CSV com o cabeçalho e define o início da medição |
| 4 | `Set up Python` | Configura o Python 3.12 no ambiente do runner |
| 5 | `Make measure script executable` | Concede permissão de execução ao script `measure_step.sh` |
| 6 | `Install dependencies` | Instala as dependências da aplicação FastAPI, etapa medida como `install_dependencies` |
| 7 | `Run unit tests` | Executa os testes unitários com pytest, etapa medida como `unit_tests` |
| 8 | `Run SonarQube SAST analysis` | Executa a análise SAST via SonarScanner CLI, etapa medida como `sonarqube_sast` |
| 9 | `Build Docker image` | Constrói a imagem Docker da aplicação, etapa medida como `docker_build` |
| 10 | `Install kind` | Instala o `kind` em `$HOME/.local/bin` |
| 11 | `Create kind cluster` | Cria o cluster Kubernetes local, medido como parte do deploy |
| 12 | `Deploy to Kubernetes` | Aplica os manifests e aguarda o rollout, etapa medida como `kubernetes_deploy` |
| 13 | `Kubernetes smoke test` | Verifica disponibilidade da aplicação via `curl`, etapa medida como `kubernetes_smoke_test` |
| 14 | `Record workflow total duration` | Registra o tempo total do pipeline no CSV como `workflow_total` |
| 15 | `Display metrics` | Exibe o CSV de resultados no log do workflow |
| 16 | `Write job summary` | Escreve o resumo do run no GitHub Actions Summary |
| 17 | `Upload CSV artifact` | Envia o CSV como artifact para download |

#### Posicionamento da etapa de SAST

A etapa `sonarqube_sast` foi inserida entre `unit_tests` e `docker_build`. Essa sequência é tecnicamente coerente: a análise estática deve ocorrer sobre o código-fonte antes que ele seja empacotado em imagem, refletindo um pipeline DevSecOps com prática de segurança antecipada, conhecida como **shift-left security**.

A composição operacional do C2 self-hosted fica representada por:

```text
C2 self-hosted = install_dependencies
               + unit_tests
               + sonarqube_sast
               + docker_build
               + kubernetes_deploy
               + kubernetes_smoke_test
               + workflow_total
```

---

<a id="decisao-self-hosted-runner"></a>
## 🖥️ Decisão: self-hosted runner

### Contexto

O pipeline C1 original utilizava um GitHub-hosted runner:

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
| SonarQube | Container Docker local, rede `sonarqube_default` |

### ⚠️ Limitação metodológica identificada

A mudança do tipo de runner entre o C1 original e o C2 representa uma diferença no ambiente de execução, o que precisa ser reconhecido como **limitação metodológica** do experimento.

Se o C1 original, executado em `ubuntu-latest`, fosse comparado diretamente com o C2 executado em `self-hosted`, a diferença de tempo entre os cenários poderia ser influenciada não apenas pela etapa `sonarqube_sast`, mas também por variáveis externas relacionadas ao ambiente de execução.

Entre essas variáveis, destacam-se:

- runner hospedado pelo GitHub versus runner local;
- diferenças de hardware;
- persistência de estado no self-hosted runner;
- cache;
- rede;
- comportamento do Docker;
- containers antigos;
- execução local em WSL 2;
- diferenças no tempo de criação do ambiente.

Portanto, comparar diretamente `C1 ubuntu-latest` com `C2 self-hosted` enfraqueceria a validade interna do experimento, pois dificultaria atribuir a diferença de lead time exclusivamente à inclusão da análise SAST.

Essa constatação levou à decisão metodológica complementar documentada na próxima seção.

---

<a id="controle-experimental-comparacao-entre-c1-self-hosted-e-c2-self-hosted"></a>
## 🧪 Controle experimental: comparação entre C1 self-hosted e C2 self-hosted

Durante a validação metodológica do C2, foi adotada uma decisão de controle experimental dentro da própria Etapa 6:

```text
Comparar C1 self-hosted com C2 self-hosted.
```

Essa decisão não cria uma nova etapa no projeto. Ela complementa a Etapa 6 com um baseline executado no mesmo ambiente do C2, permitindo que a comparação entre os cenários seja metodologicamente mais justa.

### Definição dos cenários comparáveis

| Cenário | Definição | Runner | SAST |
|---|---|---|---|
| `C1 self-hosted` | Pipeline baseline sem SonarQube, executado no mesmo ambiente local do C2 | `self-hosted` | Não |
| `C2 self-hosted` | Pipeline baseline com adição da etapa `sonarqube_sast` | `self-hosted` | Sim |

A relação entre os cenários pode ser representada da seguinte forma:

```text
C1 self-hosted = pipeline baseline sem SAST, executado no mesmo self-hosted runner do C2
C2 self-hosted = mesmo pipeline baseline, adicionando a etapa sonarqube_sast
```

Essa estrutura melhora a validade interna do experimento porque reduz variáveis externas e torna mais defensável atribuir a diferença de tempo principalmente à inclusão da análise SAST com SonarQube.

### Novo workflow criado para o baseline controlado

Foi criado o workflow:

```text
.github/workflows/c1-baseline-self-hosted.yml
```

Esse workflow representa o baseline C1 executado no mesmo ambiente local do C2. Ele utiliza:

```yaml
runs-on: self-hosted
```

E mantém as mesmas etapas principais do C1 original, sem incluir SonarQube:

```text
install_dependencies
unit_tests
docker_build
kubernetes_deploy
kubernetes_smoke_test
workflow_total
```

O workflow C2 executa as mesmas etapas e adiciona exclusivamente:

```text
sonarqube_sast
```

### Diferença metodológica entre C1 original e C1 self-hosted

O C1 original continua sendo parte do histórico experimental do projeto, mas, para a comparação direta com o C2 self-hosted, o baseline mais adequado passa a ser o C1 self-hosted.

| Comparação | Situação metodológica | Observação |
|---|---|---|
| `C1 ubuntu-latest` × `C2 self-hosted` | Menos controlada | Mistura diferença de ferramenta com diferença de ambiente |
| `C1 self-hosted` × `C2 self-hosted` | Mais controlada | Mantém o mesmo runner e isola melhor o impacto do SAST |

Assim, a análise oficial da Etapa 6 deverá considerar como comparação principal:

```text
Δ = C2 self-hosted − C1 self-hosted
```

Esse delta representa o incremento de tempo observado ao adicionar a etapa `sonarqube_sast` ao pipeline baseline, mantendo o mesmo ambiente de execução.

---

<a id="problemas-encontrados-e-ajustes-realizados"></a>
## 🛠️ Problemas encontrados e ajustes realizados

Durante a implementação do cenário C2, foram identificados e solucionados cinco problemas. Cada um é documentado abaixo com o contexto, o erro observado e a solução adotada.

---

### Problema 1 — Dependência `libicu` ausente no Ubuntu 26.04

**Contexto:** A primeira tentativa de configurar o self-hosted runner foi realizada em uma instância do Ubuntu 26.04 no WSL 2.

**Erro:**

```text
Libicu's dependencies is missing for Dotnet Core 6.0
```

**Causa:** O Ubuntu 26.04 possui uma versão de `libicu` incompatível com as dependências esperadas por componentes internos do runner do GitHub Actions.

**Solução:** O ambiente foi recriado utilizando **Ubuntu 24.04 LTS**, que possui a versão compatível da biblioteca. Após a reinstalação do runner nessa versão, o problema não ocorreu.

---

### Problema 2 — Docker não disponível no WSL 2

**Contexto:** Após configurar o Ubuntu 24.04 no WSL 2, o comando `docker` não estava disponível na sessão do runner.

**Erro:**

```text
The command 'docker' could not be found in this WSL 2 distro.
```

**Causa:** O Docker Desktop não estava integrado à distribuição Ubuntu do WSL 2.

**Solução:** A integração foi habilitada pelo painel do Docker Desktop:

```text
Docker Desktop > Settings > Resources > WSL Integration > Enable for Ubuntu
```

Após reiniciar a sessão WSL, os comandos `docker version`, `docker ps` e `docker compose version` passaram a funcionar corretamente no ambiente do runner.

---

### Problema 3 — SonarScanner não conseguia acessar o SonarQube

**Contexto:** O SonarQube estava em execução e acessível via navegador em `http://localhost:9000`. No entanto, ao executar o SonarScanner dentro de um container Docker, a análise falhava ao tentar se conectar ao servidor.

**Causa:** Dentro de um container Docker, o endereço `localhost` referencia o próprio container — não o host nem os outros containers. O SonarScanner, executado em um container isolado, não conseguia alcançar o SonarQube por esse endereço.

**Solução:**

1. Identificar a rede Docker à qual o SonarQube pertence:

   ```text
   sonarqube_default
   ```

2. Verificar o nome do serviço SonarQube na rede:

   ```text
   tcc-sonarqube
   ```

3. Testar a conectividade entre containers usando o nome do serviço:

   ```text
   http://tcc-sonarqube:9000
   ```

4. Atualizar o secret `SONAR_HOST_URL` para:

   ```text
   http://tcc-sonarqube:9000
   ```

5. Ajustar o workflow para conectar o container do SonarScanner à mesma rede Docker do SonarQube:

   ```bash
   --network "$SONARQUBE_NETWORK"
   ```

---

### Problema 4 — Instalação do `kind` solicitava senha (`sudo`)

**Contexto:** A etapa de instalação do `kind` utilizava `sudo` para mover o binário para `/usr/local/bin`.

**Problema:** No ambiente do self-hosted runner sem TTY interativo, o `sudo` aguardava entrada de senha, causando timeout na etapa e potencialmente interferindo na medição do lead time.

**Solução:**

- Remover o uso de `sudo` da etapa de instalação.
- Instalar o binário do `kind` em um diretório com permissão de escrita pelo usuário:

  ```text
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

```text
ERROR: failed to create cluster: node(s) already exist for a cluster with the name "tcc-devsecops"
```

**Causa:** O container Docker do nó do cluster `kind` da execução anterior permanecia ativo, impedindo a criação de um novo cluster com o mesmo nome.

**Solução:** Adição de uma etapa de limpeza explícita **antes** do início da medição do pipeline:

```yaml
- name: Cleanup previous kind cluster container
  run: |
    docker rm -f "${CLUSTER_NAME}-control-plane" 2>/dev/null || true
```

> [!NOTE]
> **Decisão de posicionamento:** Essa etapa foi inserida **antes** do passo `Prepare results CSV`, que marca o início da janela de medição. Dessa forma, o tempo de limpeza do ambiente não é contabilizado no lead time do pipeline, garantindo que a medição reflita apenas a execução do pipeline em si.

---

<a id="validacao-tecnica-dos-cenarios-self-hosted"></a>
## ✅ Validação técnica dos cenários self-hosted

Após a resolução dos problemas documentados na seção anterior, foram realizados runs de validação para confirmar que os workflows executam de ponta a ponta no ambiente self-hosted.

É importante destacar que os runs apresentados nesta seção têm finalidade de **validação técnica**, e não de conclusão experimental. Eles demonstram que os workflows estão funcionais, que os artifacts são gerados corretamente e que os CSVs possuem o formato esperado. Os dados desses runs não devem ser tratados como resultados oficiais definitivos do TCC.

---

### Validação técnica do C2 self-hosted

Foi realizado um run de validação para confirmar que o workflow C2 executa de ponta a ponta com a etapa de análise SAST via SonarQube.

#### Resultado da validação do C2

| Item | Resultado |
|---|---|
| Status do workflow | ✅ Sucesso |
| Todas as etapas concluídas | ✅ Sim |
| Pedido de senha durante execução | ✅ Não |
| Artifact disponível para download | ✅ Sim |
| GitHub Actions Summary com CSV | ✅ Sim |
| SonarQube acessível durante análise | ✅ Sim |
| Quality Gate disponível no SonarQube | ✅ Sim |
| Etapa `sonarqube_sast` presente no CSV | ✅ Sim |

#### Identificação do run de validação do C2

```text
run_id:     26893629530
run_number: 3
commit_sha: 2d200ff6537e1fa9f33878acdf5e4afc2cf0d174
```

#### CSV coletado no run de validação do C2

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

#### Tempos por etapa do C2 — run de validação

| Etapa | Duração |
|---|---:|
| `install_dependencies` | 0 s |
| `unit_tests` | 1 s |
| `sonarqube_sast` | **15 s** |
| `docker_build` | 3 s |
| `kubernetes_deploy` | 39 s |
| `kubernetes_smoke_test` | 5 s |
| **`workflow_total`** | **94 s** |

> [!NOTE]
> Este run foi realizado durante o processo de ajuste do ambiente e do workflow. Por isso, é classificado como **validação técnica**, não como amostra experimental oficial. Os dados coletados neste run **não serão utilizados como conclusão definitiva** na análise comparativa do TCC.

---

### Validação técnica do C1 self-hosted

Também foi executado um run de validação do workflow C1 self-hosted, criado para representar o baseline sem SAST no mesmo ambiente local do C2.

#### Resultado da validação do C1 self-hosted

| Item | Resultado |
|---|---|
| Status do workflow | ✅ Sucesso |
| Pedido de senha durante execução | ✅ Não |
| Artifact gerado | ✅ Sim |
| GitHub Actions Summary com CSV | ✅ Sim |
| Etapa `sonarqube_sast` ausente no CSV | ✅ Sim |
| Caracterização como baseline sem SAST | ✅ Confirmada |

A ausência da etapa `sonarqube_sast` no CSV confirma que esse workflow representa o baseline sem análise SAST, servindo como controle para a comparação com o C2 self-hosted.

#### Identificação do run de validação do C1 self-hosted

```text
run_id:     26901717913
run_number: 1
commit_sha: 9c7566ff2a61faf66e1ce7f759e8d71dc55103fc
```

#### CSV coletado no run de validação do C1 self-hosted

```csv
scenario,run_id,run_number,commit_sha,step_name,start_timestamp,end_timestamp,duration_seconds,status
C1-self-hosted,26901717913,1,9c7566ff2a61faf66e1ce7f759e8d71dc55103fc,install_dependencies,2026-06-03T17:32:14Z,2026-06-03T17:32:15Z,1,success
C1-self-hosted,26901717913,1,9c7566ff2a61faf66e1ce7f759e8d71dc55103fc,unit_tests,2026-06-03T17:32:15Z,2026-06-03T17:32:15Z,0,success
C1-self-hosted,26901717913,1,9c7566ff2a61faf66e1ce7f759e8d71dc55103fc,docker_build,2026-06-03T17:32:15Z,2026-06-03T17:32:18Z,3,success
C1-self-hosted,26901717913,1,9c7566ff2a61faf66e1ce7f759e8d71dc55103fc,kubernetes_deploy,2026-06-03T17:32:48Z,2026-06-03T17:33:24Z,36,success
C1-self-hosted,26901717913,1,9c7566ff2a61faf66e1ce7f759e8d71dc55103fc,kubernetes_smoke_test,2026-06-03T17:33:24Z,2026-06-03T17:33:29Z,5,success
C1-self-hosted,26901717913,1,9c7566ff2a61faf66e1ce7f759e8d71dc55103fc,workflow_total,2026-06-03T17:32:14Z,2026-06-03T17:33:29Z,75,success
```

#### Tempos por etapa do C1 self-hosted — run de validação

| Etapa | Duração |
|---|---:|
| `install_dependencies` | 1 s |
| `unit_tests` | 0 s |
| `docker_build` | 3 s |
| `kubernetes_deploy` | 36 s |
| `kubernetes_smoke_test` | 5 s |
| **`workflow_total`** | **75 s** |

#### Resumo do run de validação do C1 self-hosted

| Métrica | Valor |
|---|---:|
| Run ID | 26901717913 |
| Run number | 1 |
| Commit | `9c7566ff2a61faf66e1ce7f759e8d71dc55103fc` |
| `workflow_total` | 75 segundos |
| Status | success |

---

### Comparação inicial entre validações técnicas

A tabela abaixo apresenta uma comparação inicial apenas entre os runs de validação técnica já executados:

| Cenário | `workflow_total` | Observação |
|---|---:|---|
| C1 self-hosted validação | 75 segundos | Baseline sem SAST |
| C2 self-hosted validação | 94 segundos | Baseline com `sonarqube_sast` |

Diferença observada na validação:

```text
94s - 75s = 19s
```

Essa diferença é coerente com a expectativa de que a adição de uma etapa de análise SAST aumente o tempo total do pipeline. Porém, ela **não deve ser tratada como conclusão final**, pois foi obtida em runs de validação técnica, não em amostras oficiais estabilizadas.

A conclusão experimental deverá ser baseada na coleta oficial, composta por cinco execuções do C1 self-hosted e cinco execuções do C2 self-hosted.



---

*Documentação gerada para o TCC: "Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD"*
