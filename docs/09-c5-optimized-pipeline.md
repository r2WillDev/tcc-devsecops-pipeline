# Etapa 9 — C5: Pipeline Otimizado

<!-- Observação interna: revisar prints e atualizar caminhos das evidências antes de abrir o PR. -->

> **TCC:** Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD
> **Repositório:** [r2WillDev/tcc-devsecops-pipeline](https://github.com/r2WillDev/tcc-devsecops-pipeline)
> **Branch:** `feature/c5-optimized-pipeline`
> **Status:** :white_check_mark: Concluída — aguardando PR

---

## Sumário

- [Objetivo da Etapa](#objetivo-da-etapa)
- [Contexto Experimental](#contexto-experimental)
- [Arquivos Criados e Modificados](#arquivos-criados-e-modificados)
- [Otimizações Aplicadas](#otimizações-aplicadas)
- [Problemas Encontrados e Solução](#problemas-encontrados-e-solução)
- [Resultados das 5 Execuções Oficiais](#resultados-das-5-execuções-oficiais)
- [Estatísticas Consolidadas](#estatísticas-consolidadas)
- [Comparação C4 vs C5](#comparação-c4-vs-c5)
- [Resultados de Segurança](#resultados-de-segurança)
- [Observações Metodológicas](#observações-metodológicas)

---

## Objetivo da Etapa

A Etapa 9 tem como objetivo criar, executar e documentar o cenário **C5 — Pipeline Otimizado**, uma versão aperfeiçoada do cenário C4 que **preserva integralmente as práticas DevSecOps** (SAST, SCA e DAST), mas aplica otimizações controladas para **reduzir o overhead operacional** e melhorar o lead time do pipeline CI/CD.

> [!IMPORTANT]
> O C5 **não remove** nenhuma ferramenta de segurança. O SonarQube SAST, o Trivy SCA e o OWASP ZAP DAST **continuaram ativos** em todas as execuções oficiais. As otimizações foram aplicadas na camada de infraestrutura e orquestração do pipeline, não na cobertura de segurança.

A métrica principal de lead time neste experimento é o `workflow_total`, que representa o tempo total de execução do pipeline do início ao fim. As demais etapas são métricas operacionais individuais e **não** devem ser somadas ao `workflow_total` para evitar dupla contagem.

---

## Contexto Experimental

O experimento é estruturado em cinco cenários progressivos de pipeline CI/CD:

| Cenário | Descrição | Ferramentas de Segurança |
| ------- | --------- | ------------------------ |
| **C1** | Pipeline Baseline | Nenhuma |
| **C2** | Pipeline com SAST | SonarQube |
| **C3** | Pipeline com SAST + SCA | SonarQube + Trivy |
| **C4** | Pipeline com SAST + SCA + DAST | SonarQube + Trivy + OWASP ZAP |
| **C5** | Pipeline Otimizado | SonarQube + Trivy + OWASP ZAP *(com otimizações)* |

O **C5** é comparado **principalmente com o C4**, pois ambos possuem a mesma cobertura de segurança. O objetivo da comparação é quantificar o impacto das otimizações no lead time sem comprometer a postura de segurança do pipeline.

O ambiente de execução utilizou:

- Runner **self-hosted** (`tcc-wsl-runner`)
- **WSL 2** com Ubuntu 24.04
- **Docker Desktop** com integração WSL ativa
- **kind** para cluster Kubernetes local
- **SonarQube** Community Edition em container Docker
- **OWASP ZAP** em execução automatizada

---

## Arquivos Criados e Modificados

| Arquivo | Ação | Finalidade |
| ------- | ---- | ---------- |
| [`.github/workflows/c5-optimized.yml`](../.github/workflows/c5-optimized.yml) | Criado | Workflow do cenário C5 com otimizações |
| [`analysis/raw/c5_optimized.csv`](../analysis/raw/c5_optimized.csv) | Criado | Armazenamento das métricas brutas das execuções C5 |
| [`docs/09-c5-optimized-pipeline.md`](../docs/09-c5-optimized-pipeline.md) | Criado | Documentação desta etapa |

> [!NOTE]
> O script `ci/scripts/measure_step.sh` **não foi modificado**. O comportamento de medição, registro de status e fail-fast herdado das etapas anteriores foi reaproveitado sem alteração.

### Commits realizados

| Hash | Mensagem |
| ---- | -------- |
| `18e1e93` | `analysis: add C5 results CSV header` |
| `ce7f225` | `ci: add initial C5 optimized workflow` |
| `4e1ab5d` | `ci: add Python dependency cache to C5 workflow` |
| `e935bab` | `ci: add Trivy cache to optimized pipeline` |
| `5fb08dc` | `ci: add conditional DAST execution to C5 workflow` |

Adicionalmente, foi realizado um ajuste posterior:

```text
ci: force JavaScript actions to Node 24 in C5 workflow
```

Esse commit adicionou a variável de ambiente `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` ao workflow. Com isso, o aviso sobre Node.js 20 passou a ser apenas informativo — as actions JavaScript foram forçadas a executar com Node.js 24, garantindo compatibilidade futura com a plataforma GitHub Actions.

---

## Otimizações Aplicadas

| Otimização | Implementação | Impacto esperado | Evidência |
| ---------- | ------------- | ---------------- | --------- |
| Cache de dependências Python | `actions/setup-python@v6` com `cache: "pip"` | Elimina o download repetido de pacotes PyPI entre execuções | `Cache restored successfully` nos logs |
| Cache do banco de dados Trivy | `actions/cache@v4` em `~/.cache/trivy` | Evita download repetido do banco de vulnerabilidades | `Cache hit occurred on the primary key Linux-trivy-v0.71.0-...` |
| Execução condicional do OWASP ZAP | Input `run_zap` com padrão `"true"` | Permite execuções manuais econômicas sem comprometer dados oficiais | Parâmetro `run_zap` visível no `workflow_dispatch` |
| Fail-fast herdado | Comportamento do `measure_step.sh` | Encerra o pipeline imediatamente quando uma etapa crítica falha, evitando execução de etapas pesadas desnecessárias | Comportamento observado em tentativas com falha |
| Compatibilidade futura Node.js 24 | `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` | Prepara o workflow para a descontinuação do Node.js 20 nas actions | Warning informativo nos logs de execução |

### Detalhamento das otimizações

#### 1. Cache de dependências Python

O cache foi configurado usando `actions/setup-python@v6` com os parâmetros:

```yaml
- name: Setup Python with pip cache
  uses: actions/setup-python@v6
  with:
    python-version: "3.12"
    cache: "pip"
    cache-dependency-path: "app/requirements.txt"
```

Evidência de cache hit nos logs:

```text
Cache hit for: setup-python-Linux-x64-24.04-Ubuntu-python-3.12.13-pip-...
Cache restored successfully
```

#### 2. Cache do Trivy

O banco de dados de vulnerabilidades do Trivy foi cacheado usando `actions/cache@v4`:

```yaml
- name: Cache Trivy vulnerability database
  uses: actions/cache@v4
  with:
    path: ~/.cache/trivy
    key: ${{ runner.os }}-trivy-${{ env.TRIVY_VERSION }}-${{ hashFiles('ci/config/trivy.yaml') }}
    restore-keys: |
      ${{ runner.os }}-trivy-${{ env.TRIVY_VERSION }}-
```

Evidência de cache hit nos logs:

```text
Cache hit occurred on the primary key Linux-trivy-v0.71.0-...
```

#### 3. Execução condicional do OWASP ZAP

O input `run_zap` foi adicionado ao `workflow_dispatch`, com valor padrão `"true"`:

```yaml
on:
  workflow_dispatch:
    inputs:
      run_zap:
        description: "Run OWASP ZAP DAST scan"
        required: true
        default: "true"
        type: choice
        options:
          - "true"
          - "false"
```

> [!WARNING]
> A execução condicional do ZAP **não foi usada para reduzir artificialmente o tempo** das execuções oficiais. Nas 5 execuções coletadas para o experimento, o `run_zap` manteve o valor padrão `"true"` e o DAST foi executado normalmente. A condicional existe apenas para facilitar execuções de teste manual sem custo de tempo, sem impactar os dados experimentais.

Quando `run_zap=false`, as etapas de DAST registram métricas com status `skipped`, preservando a comparabilidade estrutural do CSV.

#### 4. Fail-fast herdado

O script `ci/scripts/measure_step.sh` registra o status de cada etapa e, em caso de falha, encerra com `exit 1`. Esse comportamento evita que etapas pesadas como o ZAP sejam executadas após uma falha crítica anterior, reduzindo o desperdício de tempo em runs com erro.

#### 5. Compatibilidade futura com Node.js 24

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
```

O warning sobre Node.js 20 permaneceu nos logs apenas como aviso informativo. Com essa variável ativa, as actions que ainda usavam o runtime Node.js 20 passaram a ser executadas com Node.js 24, preparando o workflow para a descontinuação futura do Node.js 20 na plataforma GitHub Actions.



## Problemas Encontrados e Solução

### Falha na etapa `Run SonarQube SAST analysis`

<details>
<summary>:warning: Expandir detalhes do problema e solução</summary>

#### Erro observado

```text
failed to connect to the docker API at unix:///var/run/docker.sock
```

#### Causa raiz

O runner `tcc-wsl-runner` estava em execução dentro do WSL, mas o **Docker Desktop** não estava ativo ou a integração com a distro `Ubuntu-24.04` havia sido desativada. Como consequência:

- O socket `/var/run/docker.sock` não estava disponível no WSL
- O SonarQube Scanner não conseguia se comunicar com o daemon Docker
- A etapa de SAST falhou antes de completar a análise

#### Solução aplicada

1. Reiniciar o Docker Desktop no Windows
2. Aguardar inicialização completa do daemon Docker
3. Verificar e ativar a integração Docker Desktop → WSL2 → `Ubuntu-24.04`
4. Confirmar a presença do socket no WSL:

   ```bash
   ls -l /var/run/docker.sock
   ```

5. Subir novamente o container do SonarQube:

   ```powershell
   docker compose -f .\infra\sonarqube\docker-compose.yml up -d
   ```

6. Aguardar o SonarQube ficar `UP`:

   ```powershell
   Invoke-RestMethod http://localhost:9000/api/system/status
   ```

7. Reiniciar o runner no WSL:

   ```bash
   cd ~/actions-runner-tcc
   ./run.sh
   ```

#### Resultado

- Runner voltou a ouvir e processar jobs
- Docker ficou acessível no WSL via socket
- SonarQube retornou ao status `UP`
- O workflow C5 executou com sucesso nas execuções subsequentes

</details>

---

## Resultados das 5 Execuções Oficiais


Os dados abaixo foram extraídos dos artifacts gerados pelo GitHub Actions, especialmente do arquivo `analysis/raw/c5_optimized_run.csv`, produzido em cada execução oficial do workflow C5. O arquivo versionado `analysis/raw/c5_optimized.csv` contém apenas o cabeçalho base para padronização dos dados.

| Run | `workflow_total` | `dast_zap_baseline` | `kubernetes_deploy` | `sonarqube_sast` | Status |
| --: | ---------------: | ------------------: | ------------------: | ---------------: | ------ |
| 1 | 172 | 44 | 39 | 16 | :white_check_mark: success |
| 2 | 240 | 79 | 37 | 12 | :white_check_mark: success |
| 3 | 180 | 44 | 29 | 20 | :white_check_mark: success |
| 4 | 178 | 37 | 34 | 13 | :white_check_mark: success |
| 5 | 189 | 36 | 38 | 18 | :white_check_mark: success |

### Dados brutos completos (CSV)

<details>
<summary>Expandir CSV completo</summary>

```csv
run,install_dependencies,unit_tests,sonarqube_sast,docker_build,sca_fs,sca_image,sca_total,kubernetes_deploy,kubernetes_smoke_test,dast_health_check,dast_zap_baseline,workflow_total
1,0,2,16,5,0,1,1,39,5,0,44,172
2,1,1,12,2,1,0,1,37,6,0,79,240
3,1,1,20,2,0,3,3,29,5,0,44,180
4,0,1,13,2,0,2,2,34,5,0,37,178
5,0,2,18,2,0,2,2,38,5,0,36,189
```

</details>

---

## Estatísticas Consolidadas

> [!NOTE]
> O `workflow_total` é a **métrica principal de lead time** do experimento e **não** é incluído no ranking de etapas operacionais. As médias abaixo são calculadas sobre as 5 execuções oficiais.

| Métrica | Resultado |
| ------- | --------: |
| `workflow_total` médio | **191,80 s** |
| `workflow_total` mínimo | 172,00 s |
| `workflow_total` máximo | 240,00 s |
| Variação (`max - min`) | 68,00 s |
| Desvio padrão amostral | 27,63 s |
| Etapa operacional mais lenta | `dast_zap_baseline` — 48,00 s |
| Segunda etapa mais lenta | `kubernetes_deploy` — 35,40 s |

### Ranking das etapas operacionais por média (s)

> `workflow_total` **excluído** do ranking por ser a métrica agregada de lead time.

| Posição | Etapa | Média (s) |
| ------: | ----- | --------: |
| 1 | `dast_zap_baseline` | **48,00** |
| 2 | `kubernetes_deploy` | **35,40** |
| 3 | `sonarqube_sast` | 15,80 |
| 4 | `kubernetes_smoke_test` | 5,20 |
| 5 | `docker_build` | 2,60 |
| 6 | `sca_total` | 1,80 |
| 7 | `sca_image` | 1,60 |
| 8 | `unit_tests` | 1,40 |
| 9 | `install_dependencies` | 0,40 |
| 10 | `sca_fs` | 0,20 |
| 11 | `dast_health_check` | 0,00 |

---

## Comparação C4 vs C5

<a id="comparacao-c4-c5"></a>

> [!IMPORTANT]
> A comparação entre C4 e C5 é o principal indicador do impacto das otimizações aplicadas, **mantendo a mesma cobertura de segurança** (SAST + SCA + DAST).

| Métrica | C4 (referência) | C5 (médio) | Redução absoluta | Redução percentual |
| ------- | --------------: | ---------: | ---------------: | -----------------: |
| `workflow_total` | 309 s | 191,80 s | **117,20 s** | **37,93%** |
| `dast_zap_baseline` | 197 s | 48,00 s | **149,00 s** | **75,63%** |

### Análise da redução

A redução de **~37,93%** no `workflow_total` do C5 em relação ao C4 de referência não deve ser atribuída exclusivamente ao cache. Os fatores que contribuíram para a melhora incluem:

- :rocket: **Cache de dependências Python** — eliminou o download repetido de pacotes PyPI
- :rocket: **Cache do banco de dados Trivy** — eliminou o download repetido do banco de CVEs
- :rocket: **Ambiente aquecido** — o runner self-hosted manteve dados de camadas Docker e artefatos locais entre execuções
- :rocket: **Variações naturais do runner local** — o ambiente WSL + Docker Desktop apresenta variabilidade inerente
- :rocket: **Menor overhead operacional** — a soma das otimizações reduziu o tempo de preparação de cada etapa

A redução expressiva do `dast_zap_baseline` pode estar relacionada ao aquecimento do ambiente local, reaproveitamento de camadas/imagens Docker, menor overhead do runner self-hosted e variações naturais da execução do ZAP em ambiente WSL + Docker Desktop.


---

## Resultados de Segurança

O C5 manteve plena cobertura de segurança. Os resultados abaixo confirmam que as ferramentas continuaram operacionais e reportando achados.

### Trivy SCA

| Alvo | Low | Medium | High | Critical | Total |
| ---- | --: | -----: | ---: | -------: | ----: |
| Filesystem | — | 1 | — | — | 1 |
| Image | 63 | 33 | 8 | 2 | **106** |
| **Total** | **63** | **34** | **8** | **2** | **107** |

> [!NOTE]
> O total agregado soma os achados por alvo de análise (`filesystem` e `image`) e não representa necessariamente vulnerabilidades únicas deduplicadas entre os dois scans.


> [!NOTE]
> As vulnerabilidades reportadas pelo Trivy são consistentes com os resultados dos cenários anteriores (C3 e C4), confirmando que o C5 não alterou o escopo de análise de dependências.

### OWASP ZAP DAST

| Info | Low | Medium | High | Total |
| ---: | --: | -----: | ---: | ----: |
| 1 | 2 | 0 | 0 | **3** |


> [!NOTE]
> Nenhuma vulnerabilidade de severidade **Medium** ou **High** foi identificada pelo ZAP. O resultado está alinhado com os cenários anteriores, confirmando que a aplicação FastAPI de teste mantém o mesmo perfil de exposição.



## Observações Metodológicas

1. **`workflow_total` como métrica de lead time:** o `workflow_total` representa o tempo total decorrido desde o início do workflow até sua conclusão. É a métrica que mais se aproxima do conceito de *lead time* em CI/CD. As demais métricas são etapas operacionais individuais e servem para diagnóstico, não para ranking de lead time.

2. **Não atribuir todo o ganho ao cache:** as otimizações de cache são uma parte do ganho, mas o ambiente aquecido (runner self-hosted que mantém estado entre runs), as variações naturais do WSL e do Docker Desktop, e a menor sobrecarga operacional agregada também contribuíram para a redução observada.

3. **Comparabilidade dos dados:** as 5 execuções oficiais do C5 foram realizadas com `run_zap=true` (valor padrão), garantindo que o DAST esteve ativo em todas as medições. Execuções de teste manual com `run_zap=false` não foram incluídas nos dados experimentais.

4. **Variabilidade esperada:** o desvio padrão amostral de 27,63 s (sobre uma média de 191,80 s) é esperado em ambientes self-hosted locais. A run 2 apresentou o maior `workflow_total` (240 s), puxado pelo `dast_zap_baseline` de 79 s, o que é consistente com a variabilidade do ZAP em ambientes locais.

5. **Preservação das práticas DevSecOps:** o C5 demonstra que é possível **reduzir o lead time de um pipeline DevSecOps sem abrir mão das verificações de segurança**. Esse é o ponto central da contribuição do cenário C5 para o experimento.

> O C5 preservou SAST, SCA e DAST, aplicando otimizações controladas para reduzir overhead operacional e melhorar o lead time sem eliminar práticas de segurança.



### Notas de rodapé

O `workflow_total` é calculado pelo script `measure_step.sh` como a diferença entre o timestamp de início do job e o timestamp de conclusão da última etapa medida.[^1]

O desvio padrão amostral foi calculado com `n-1` no denominador (fórmula de Bessel), adequado para amostras pequenas.[^2]
[^1]: O script `ci/scripts/measure_step.sh` registra timestamps em epoch Unix e calcula a duração em segundos inteiros por diferença simples.

[^2]: Fórmula: s = √(Σ(xᵢ − x̄)² / (n − 1)), onde n = 5 execuções e x̄ = 191,80 s.
    O uso de n-1 é recomendado quando a amostra é pequena e o objetivo é estimar o desvio padrão populacional a partir de uma amostra.

---

*Documento gerado para o TCC — Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD.*<br>