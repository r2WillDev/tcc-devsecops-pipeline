# Etapa 8 — C4: Adicionar OWASP ZAP como DAST

Esta documentação registra a implementação da Etapa 8 do TCC, na qual foi adicionada a prática de DAST ao pipeline DevSecOps já composto por SAST e SCA. No cenário C4, o pipeline passa a executar SonarQube, Trivy e OWASP ZAP, permitindo avaliar o impacto da análise dinâmica de segurança no lead time do fluxo CI/CD.

## Sumário

- [1. Visão geral da etapa](#1-visão-geral-da-etapa)
- [2. Objetivo do C4](#2-objetivo-do-c4)
- [3. Conceitos utilizados](#3-conceitos-utilizados)
  - [3.1 SAST](#31-sast)
  - [3.2 SCA](#32-sca)
  - [3.3 DAST](#33-dast)
  - [3.4 OWASP ZAP Baseline Scan](#34-owasp-zap-baseline-scan)
  - [3.5 Report-only](#35-report-only)
- [4. Decisões técnicas](#4-decisões-técnicas)
- [5. Branch e arquivos criados](#5-branch-e-arquivos-criados)
- [6. Comandos executados](#6-comandos-executados)
- [7. Estrutura do workflow C4](#7-estrutura-do-workflow-c4)
- [8. Configuração do OWASP ZAP](#8-configuração-do-owasp-zap)
- [9. Garantia de disponibilidade da aplicação antes do DAST](#9-garantia-de-disponibilidade-da-aplicação-antes-do-dast)
- [10. Problemas encontrados e correções](#10-problemas-encontrados-e-correções)
- [11. Resultados obtidos](#11-resultados-obtidos)
  - [11.1 Métricas de tempo](#111-métricas-de-tempo)
  - [11.2 Estatísticas principais](#112-estatísticas-principais)
  - [11.3 Alertas do OWASP ZAP](#113-alertas-do-owasp-zap)
  - [11.4 Resultados do Trivy no C4](#114-resultados-do-trivy-no-c4)
- [12. Artifacts gerados](#12-artifacts-gerados)
- [13. Interpretação dos resultados](#13-interpretação-dos-resultados)
- [14. Observações metodológicas](#14-observações-metodológicas)
- [15. Conclusão](#15-conclusão)

## 1. Visão geral da etapa

O C4 representa o quarto cenário experimental do TCC, adicionando análise dinâmica de segurança ao pipeline DevSecOps. Até o C3, o pipeline já executava SAST com SonarQube e SCA com Trivy. Na Etapa 8, foi incorporado o OWASP ZAP como ferramenta de DAST, permitindo analisar a aplicação em execução por meio de uma URL real.

A prática adicionada nesta etapa foi o DAST, que avalia a aplicação do ponto de vista externo, simulando interações contra o serviço já implantado. O OWASP ZAP foi escolhido por ser uma ferramenta amplamente utilizada em testes de segurança de aplicações web e por possuir modo Baseline Scan, adequado para integração inicial em pipelines CI/CD.

Dentro do experimento, o C4 permite observar o impacto incremental da inclusão do DAST em relação ao C3. Assim, a comparação central passa a ser entre um pipeline com SAST + SCA e um pipeline com SAST + SCA + DAST.

Em resumo:

| Cenário | Composição | Diferença principal |
| ------- | ---------- | ------------------- |
| C3 | SAST + SCA | Executa SonarQube e Trivy |
| C4 | SAST + SCA + DAST | Adiciona OWASP ZAP Baseline Scan |

A principal diferença em relação ao C3 é a inclusão do OWASP ZAP Baseline Scan após o deploy da aplicação em Kubernetes local e após a validação do endpoint `/health`.

## 2. Objetivo do C4

O objetivo principal do C4 é medir o impacto da análise dinâmica de segurança no lead time do pipeline CI/CD.

A pergunta principal desta etapa é:

> Quanto tempo a análise DAST com OWASP ZAP adiciona ao pipeline em relação ao C3?

O foco da etapa não foi realizar um pentest completo, mas sim integrar um DAST controlado ao fluxo CI/CD. Dessa forma, o OWASP ZAP foi utilizado em modo Baseline Scan, com geração de relatórios e coleta de métricas de tempo, sem transformar a análise em uma etapa bloqueante por alertas.

Essa abordagem mantém a coerência com o objetivo experimental do TCC: avaliar o impacto das práticas DevSecOps no tempo total do pipeline, preservando a comparabilidade entre os cenários C1, C2, C3 e C4.

## 3. Conceitos utilizados

### 3.1 SAST

SAST, ou Static Application Security Testing, é uma prática de análise de segurança realizada sobre código-fonte ou artefatos estáticos, sem executar a aplicação. No projeto, essa prática foi representada pelo SonarQube, responsável por analisar o código da aplicação e gerar evidências relacionadas à qualidade e segurança estática.

### 3.2 SCA

SCA, ou Software Composition Analysis, é a prática de análise de dependências, pacotes e imagens em busca de vulnerabilidades conhecidas. No projeto, essa prática foi representada pelo Trivy, utilizado para verificar tanto o filesystem quanto a imagem Docker da aplicação.

### 3.3 DAST

DAST, ou Dynamic Application Security Testing, é uma prática de análise de segurança aplicada sobre a aplicação em execução. Diferentemente do SAST, o DAST não analisa diretamente o código-fonte, mas sim o comportamento da aplicação exposta em uma URL real.

No C4, o DAST foi representado pelo OWASP ZAP, executado contra a aplicação implantada em Kubernetes local e exposta temporariamente por meio de `kubectl port-forward`.

### 3.4 OWASP ZAP Baseline Scan

O OWASP ZAP Baseline Scan é um modo de execução mais adequado para integração inicial em pipelines CI/CD. Ele realiza spider e passive scan, buscando identificar possíveis problemas observáveis durante a navegação e análise passiva do tráfego.

Nesta etapa, não foi executado active scan completo. A escolha do Baseline Scan está alinhada ao objetivo do C4: adicionar uma análise dinâmica controlada e mensurável, sem transformar o cenário em um teste ofensivo mais intenso.

### 3.5 Report-only

O pipeline foi configurado para reportar os alertas encontrados sem bloquear a execução inicialmente. Essa decisão preserva o foco da etapa, que é medir o impacto do DAST no lead time e coletar evidências para análise acadêmica.

> [!IMPORTANT]
> O C4 não executa active scan completo. O objetivo desta etapa é medir impacto no lead time com DAST em modo controlado.

## 4. Decisões técnicas

| Decisão | Escolha | Justificativa |
| ------- | ------- | ------------- |
| Ferramenta DAST | OWASP ZAP | Ferramenta amplamente usada para análise dinâmica |
| Modo de scan | Baseline Scan | Mais adequado ao MVP e ao CI/CD |
| Bloqueio por alertas | Não | O objetivo inicial é medir impacto, não bloquear entrega |
| Alvo do scan | Aplicação implantada em Kubernetes local | Mantém proximidade com o fluxo do C3 |
| URL alvo | `http://host.docker.internal:8000` | Permite o acesso do container ZAP ao serviço exposto via port-forward |
| Relatórios | HTML, JSON e Markdown | HTML para evidência visual, JSON para dados e Markdown para leitura |
| Artifacts | Sim | Relatórios e CSVs foram preservados como evidência |
| Comparabilidade | Mantida com C1, C2 e C3 | Foi preservado o formato padrão de métricas |

## 5. Branch e arquivos criados

A branch utilizada para o desenvolvimento da Etapa 8 foi:

```text
feature/c4-zap-dast
```

Durante a etapa, foram criados ou modificados arquivos relacionados ao workflow C4, aos CSVs de coleta de métricas e à configuração inicial do ZAP.

```text
.github/workflows/c4-sast-sca-dast.yml
analysis/raw/c4_sast_sca_dast.csv
analysis/raw/c4_zap_summary.csv
ci/config/zap-rules.tsv
```

| Arquivo | Tipo | Finalidade |
| ------- | ---- | ---------- |
| `.github/workflows/c4-sast-sca-dast.yml` | Workflow | Define o pipeline C4 com SAST, SCA e DAST |
| `analysis/raw/c4_sast_sca_dast.csv` | CSV base | Armazena o cabeçalho padronizado das métricas de tempo |
| `analysis/raw/c4_zap_summary.csv` | CSV base | Armazena o cabeçalho do resumo de alertas do ZAP |
| `ci/config/zap-rules.tsv` | Configuração | Arquivo reservado para regras do ZAP, mantido mínimo para não enviesar o experimento |

## 6. Comandos executados

Esta seção registra os principais comandos utilizados durante a preparação, diagnóstico, validação local e versionamento da Etapa 8.

Comandos de preparação da branch:

```powershell
git checkout dev
git pull origin dev
git checkout -b feature/c4-zap-dast
```

Comandos de verificação da estrutura existente:

```powershell
Test-Path .\.github\workflows\c3-sast-sca.yml
Test-Path .\ci\scripts\measure_step.sh
Test-Path .\analysis\raw\c3_sast_sca.csv
```

Comandos de build Docker e teste do endpoint `/health`:

```powershell
docker build -t tcc-devsecops-api:c4-local .\app
docker rm -f tcc-c4-health-test 2>$null
docker run -d --name tcc-c4-health-test -p 8000:8000 tcc-devsecops-api:c4-local
Start-Sleep -Seconds 5
Invoke-RestMethod http://localhost:8000/health
docker logs --tail 30 tcc-c4-health-test
docker rm -f tcc-c4-health-test
```

Comandos de SonarQube:

```powershell
docker compose -f .\infra\sonarqube\docker-compose.yml up -d
docker ps --filter "name=tcc-sonarqube"
Invoke-RestMethod http://localhost:9000/api/system/status
docker inspect tcc-sonarqube --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}'
```

Comandos de kind usados para diagnóstico:

```powershell
kind create cluster --name tcc-devsecops --config .\infra\kind\kind-cluster.yaml
kubectl cluster-info
kubectl get nodes
kind delete cluster --name tcc-devsecops
```

Comandos de Git:

```powershell
git add .\.github\workflows\c4-sast-sca-dast.yml
git add .\analysis\raw\c4_sast_sca_dast.csv
git add .\analysis\raw\c4_zap_summary.csv
git add .\ci\config\zap-rules.tsv
git commit -m "ci: add C4 SAST SCA and DAST workflow"
git commit -m "ci: align C4 Kubernetes image tag with workflow"
git push -u origin feature/c4-zap-dast
```

## 7. Estrutura do workflow C4

O workflow C4 foi estruturado para manter a base experimental dos cenários anteriores e acrescentar a etapa de DAST após a implantação da aplicação.

Sequência lógica do workflow:

1. Checkout do repositório.
2. Limpeza de cluster kind anterior.
3. Preparação dos arquivos de resultado.
4. Setup Python.
5. Instalação de dependências.
6. Execução dos testes unitários.
7. Análise SAST com SonarQube.
8. Build da imagem Docker.
9. Instalação do Trivy.
10. Scan SCA em filesystem.
11. Scan SCA em imagem.
12. Geração dos relatórios Trivy.
13. Contagem das vulnerabilidades Trivy.
14. Instalação do kind.
15. Criação do cluster Kubernetes local.
16. Deploy da aplicação no Kubernetes.
17. Smoke test do endpoint `/health`.
18. Início do port-forward para DAST.
19. Health check antes do DAST.
20. Execução do OWASP ZAP Baseline Scan.
21. Contagem dos alertas do ZAP por severidade.
22. Encerramento do port-forward.
23. Registro do tempo total do workflow.
24. Escrita do GitHub Actions Summary.
25. Upload dos artifacts.

Essa sequência garante que o ZAP seja executado somente depois que a aplicação estiver implantada e acessível, evitando medições inválidas causadas por indisponibilidade do serviço.

## 8. Configuração do OWASP ZAP

O OWASP ZAP foi executado por meio de container Docker, utilizando a imagem estável do projeto ZAP Proxy. A execução foi registrada no CSV de métricas por meio da etapa `dast_zap_baseline`.

Trecho principal do workflow:

```yaml
- name: Run OWASP ZAP baseline scan
  run: |
    ./ci/scripts/measure_step.sh "dast_zap_baseline" "$RESULTS_FILE" \
      docker run --rm \
        --add-host=host.docker.internal:host-gateway \
        -v "$GITHUB_WORKSPACE/$ZAP_REPORTS_DIR:/zap/wrk/:rw" \
        ghcr.io/zaproxy/zaproxy:stable \
        zap-baseline.py \
        -t "$ZAP_TARGET_URL" \
        -m 1 \
        -T 5 \
        -I \
        -r zap-baseline-report.html \
        -J zap-baseline-report.json \
        -w zap-baseline-report.md
```

| Opção | Significado |
| ----- | ----------- |
| `dast_zap_baseline` | Nome da etapa registrada no CSV |
| `docker run --rm` | Executa o ZAP em container temporário |
| `--add-host=host.docker.internal:host-gateway` | Permite o container acessar o host |
| `-v ...:/zap/wrk/:rw` | Mapeia o diretório dos relatórios |
| `zap-baseline.py` | Executa o Baseline Scan |
| `-t` | Define a URL alvo |
| `-m 1` | Limita o spider a 1 minuto |
| `-T 5` | Define timeout de espera |
| `-I` | Mantém o pipeline em modo report-only |
| `-r` | Gera relatório HTML |
| `-J` | Gera relatório JSON |
| `-w` | Gera relatório Markdown |

> [!WARNING]
> `localhost` dentro do container ZAP não aponta para a aplicação executada no host. Por isso, foi usado `host.docker.internal` com `--add-host=host.docker.internal:host-gateway`, permitindo que o container acesse o serviço exposto via port-forward.

## 9. Garantia de disponibilidade da aplicação antes do DAST

O DAST só foi executado após o deploy da aplicação no Kubernetes local e após a validação de disponibilidade do endpoint `/health`. Essa validação é importante para evitar que o ZAP seja executado contra uma aplicação indisponível, o que comprometeria a validade da medição.

Trecho utilizado no workflow:

```yaml
- name: Start application port-forward for DAST
  run: |
    kubectl port-forward --address 0.0.0.0 svc/tcc-api 8000:80 -n app > /tmp/c4-zap-port-forward.log 2>&1 &
    echo "PORT_FORWARD_PID=$!" >> "$GITHUB_ENV"
    sleep 5

- name: Verify application before DAST
  run: |
    ./ci/scripts/measure_step.sh "dast_health_check" "$RESULTS_FILE" \
      curl -fsS http://localhost:8000/health
```

O `port-forward` expõe temporariamente o serviço Kubernetes `svc/tcc-api` na porta `8000` do ambiente de execução. Em seguida, o health check confirma que a aplicação está acessível antes da etapa de análise dinâmica.

Essa ordem reduz o risco de falhas falsas no DAST e melhora a confiabilidade das evidências coletadas.

## 10. Problemas encontrados e correções

Durante a Etapa 8, alguns problemas foram encontrados no ambiente de execução e corrigidos antes da coleta final das evidências.

| Problema | Causa | Correção |
| -------- | ----- | -------- |
| Falha no SonarQube SAST | Container `tcc-sonarqube` estava desligado ou não estava pronto | Subir SonarQube com Docker Compose e validar `/api/system/status` |
| Falha no deploy Kubernetes | Manifesto usava `tcc-devsecops-api:local`, mas workflow carregava `tcc-devsecops-api:c4` | Adicionar `kubectl set image deployment/tcc-api tcc-api="$IMAGE_NAME" -n app` |
| Falha transitória ao criar kind cluster | `etcdserver: request timed out` durante criação do cluster | Limpar/testar cluster kind manualmente e executar novamente |
| Possível falha de acesso do ZAP ao host | Container ZAP pode não resolver o host automaticamente | Usar `--add-host=host.docker.internal:host-gateway` |
| Risco de port-forward preso | Processo em segundo plano poderia permanecer ativo | Salvar PID e encerrar no final do workflow |

> [!TIP]
> Em caso de falha no GitHub Actions, o primeiro passo é identificar exatamente em qual etapa o erro ocorreu. Isso evita alterações desnecessárias em partes do pipeline que já estavam funcionando corretamente.

## 11. Resultados obtidos

O workflow C4 executou com sucesso e gerou métricas de tempo, resumo de vulnerabilidades do Trivy, resumo de alertas do OWASP ZAP e artifacts com os relatórios produzidos durante a execução.

### 11.1 Métricas de tempo

| Run | workflow_total (s) | dast_zap_baseline (s) | zap_total_alerts |
| --- | ------------------ | --------------------- | ---------------- |
| 1 | 309 | 197 | 3 |
| 2 | 207 | 53 | 3 |
| 3 | 268 | 73 | 3 |
| 4 | 197 | 64 | 3 |
| 5 | 202 | 63 | 2 |

### 11.2 Estatísticas principais

| Métrica | Valor |
| ------- | ----- |
| Média do workflow_total | 236,60 s |
| Mediana do workflow_total | 207,00 s |
| Menor workflow_total | 197,00 s |
| Maior workflow_total | 309,00 s |
| Desvio padrão amostral do workflow_total | 49,70 s |
| Média do dast_zap_baseline | 90,00 s |
| Mediana do dast_zap_baseline | 64,00 s |
| Menor dast_zap_baseline | 53,00 s |
| Maior dast_zap_baseline | 197,00 s |
| Percentual médio do DAST no workflow_total | 38,00% |

### 11.3 Alertas do OWASP ZAP

| Run | Info | Low | Medium | High | Total |
| --- | ---- | --- | ------ | ---- | ----- |
| 1 | 1 | 2 | 0 | 0 | 3 |
| 2 | 1 | 2 | 0 | 0 | 3 |
| 3 | 1 | 2 | 0 | 0 | 3 |
| 4 | 1 | 2 | 0 | 0 | 3 |
| 5 | 1 | 1 | 0 | 0 | 2 |

O OWASP ZAP encontrou apenas alertas informacionais e baixos. Não foram registrados alertas médios ou altos nas execuções consideradas.

### 11.4 Resultados do Trivy no C4

| Alvo | Tipo | Low | Medium | High | Critical | Total |
| ---- | ---- | --- | ------ | ---- | -------- | ----- |
| Filesystem | fs | 0 | 1 | 0 | 0 | 1 |
| Imagem | image | 63 | 32 | 8 | 2 | 105 |

## 12. Artifacts gerados

Os artifacts foram baixados e validados para confirmar a preservação das evidências do C4. A estrutura validada foi:

```text
c4-sast-sca-dast-artifacts-validation-run/
├── raw/
│   ├── c4_sast_sca_dast_run.csv
│   ├── c4_trivy_summary_run.csv
│   └── c4_zap_summary_run.csv
└── reports/
    ├── trivy/
    │   ├── trivy-fs-report.json
    │   ├── trivy-fs-report.sarif
    │   ├── trivy-image-report.json
    │   └── trivy-image-report.sarif
    └── zap/
        ├── zap-baseline-report.html
        ├── zap-baseline-report.json
        ├── zap-baseline-report.md
        └── zap.yaml
```

| Artifact | Finalidade |
| -------- | ---------- |
| `c4_sast_sca_dast_run.csv` | Métricas de tempo por etapa |
| `c4_trivy_summary_run.csv` | Resumo das vulnerabilidades SCA |
| `c4_zap_summary_run.csv` | Resumo dos alertas DAST |
| `zap-baseline-report.html` | Evidência visual do relatório ZAP |
| `zap-baseline-report.json` | Dados estruturados do ZAP |
| `zap-baseline-report.md` | Relatório legível em Markdown |

## 13. Interpretação dos resultados

Os resultados obtidos no C4 confirmam a integração do DAST ao pipeline CI/CD. O pipeline passou a executar SAST com SonarQube, SCA com Trivy e DAST com OWASP ZAP, mantendo a lógica de coleta de métricas por etapa e preservando os artifacts gerados durante a execução.

A média do `workflow_total` foi de 236,60 s, enquanto a média da etapa `dast_zap_baseline` foi de 90,00 s. Considerando esses valores, o DAST representou aproximadamente 38,00% do tempo total médio do workflow, indicando impacto relevante no lead time do pipeline C4.

A primeira execução apresentou o maior tempo de ZAP, com 197 s. Nas execuções seguintes, o tempo da etapa `dast_zap_baseline` ficou entre 53 s e 73 s. Essa diferença sugere que a primeira execução pode ter sofrido maior influência de fatores de ambiente, inicialização, cache ou variações transitórias do runner.

Em relação aos alertas do OWASP ZAP, foram encontrados apenas alertas informacionais e de baixa criticidade, sem alertas médios ou altos nas execuções consideradas. O foco desta etapa foi mensuração e evidência, não correção de vulnerabilidades ou endurecimento de regras de bloqueio.

Os dados coletados no C4 serão utilizados posteriormente na comparação C3 × C4, permitindo avaliar o impacto incremental da inclusão do DAST sobre um pipeline que já possuía SAST e SCA.

## 14. Observações metodológicas

| Item | Observação |
| ---- | ---------- |
| Execuções válidas | 5 execuções/tentativas bem-sucedidas |
| Commit analisado | `a324e89326fddb6405018d1d39edf41d3480581d` |
| Branch | `feature/c4-zap-dast` |
| Métrica principal | `workflow_total` |
| Métrica específica do DAST | `dast_zap_baseline` |
| Tipo de DAST | OWASP ZAP Baseline Scan |
| Modo de bloqueio | Report-only |
| Active scan | Não utilizado |
| Comparabilidade | Mantida com C1, C2 e C3 pelo uso do mesmo CSV padrão |
| Observação sobre run_id | As medições foram realizadas no mesmo commit e podem aparecer com o mesmo `run_id`/`run_number` se tiverem sido reexecutadas no GitHub Actions |

## 15. Conclusão

A Etapa 8 foi concluída tecnicamente, pois o pipeline C4 executou SAST, SCA e DAST, coletou métricas de tempo, gerou relatórios e preservou evidências como artifacts. Com isso, o experimento passa a contar com um cenário DevSecOps mais completo para análise posterior do impacto do OWASP ZAP no lead time do pipeline CI/CD.

---


*Documentação gerada para o TCC: "Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD"*