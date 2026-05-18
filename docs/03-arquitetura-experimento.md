# 🧪 Arquitetura do Experimento

> **Arquivo:** `docs/03-arquitetura-experimento.md`
> **Projeto:** TCC — Ciência da Computação
> **Título:** Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD
> **Etapa atual:** Etapa 1 — Consolidar base do projeto
> **Status:** ⚠️ Arquitetura experimental planejada — *implementação dos pipelines pendente*

---

## 1. 🔭 Visão Geral

Este documento descreve a arquitetura experimental planejada para o TCC, cujo objetivo é avaliar como a integração de ferramentas de segurança — SAST, DAST e SCA — afeta o **lead time** de pipelines CI/CD, e como esse impacto pode ser otimizado.

A estratégia central é comparar um **pipeline baseline** (sem ferramentas de segurança) com pipelines que adicionam gradualmente camadas de análise de segurança. Um quinto cenário avaliará estratégias de otimização sobre o pipeline completo.

> [!NOTE] 
> Nenhum pipeline foi implementado até o momento. Este documento serve como referência arquitetural para as próximas etapas do projeto.

---

## 2. 🛠️ Aplicação Base

A aplicação utilizada como sistema sob teste será um **microserviço simples desenvolvido com FastAPI**.

Seu papel no experimento não é representar um sistema de negócio complexo, mas sim fornecer um ambiente controlado e reproduzível para a execução e medição dos pipelines.

| Atributo | Descrição |
|---|---|
| Framework | FastAPI (Python) |
| Containerização | Docker *(previsto — não implementado)* |
| Finalidade | Objeto experimental para coleta de métricas de pipeline |

---

## 3. 📏 Variável Principal do Experimento

A principal métrica observada será o **lead time do pipeline**, definido neste trabalho como o tempo total de execução do pipeline, do início ao término de um ciclo completo.

Além do tempo total, serão registrados os tempos individuais de cada etapa, permitindo análise granular do impacto de cada ferramenta.

---

## 4. 🗺️ Cenários Experimentais

O experimento é estruturado em **cinco cenários progressivos**, permitindo medir o impacto individual e acumulado das ferramentas de segurança.

| Cenário | Descrição resumida | Ferramentas adicionadas |
|---|---|---|
| **C1** | Pipeline baseline | — |
| **C2** | Baseline + análise estática | SonarQube (SAST) |
| **C3** | C2 + análise de dependências | Trivy (SCA) |
| **C4** | C3 + análise dinâmica | OWASP ZAP (DAST) |
| **C5** | Pipeline otimizado | Mesmas de C4 + otimizações |

---

## 5. ⚙️ Detalhamento dos Cenários

### C1 — Pipeline Baseline

Representa o pipeline inicial, sem ferramentas de análise de segurança. Serve como referência para todas as comparações.

**Etapas previstas:**

- Preparação do ambiente
- Instalação de dependências
- Execução de testes
- Build da aplicação
- Deploy ou simulação de deploy

**Objetivo:** Estabelecer o tempo base (T₀) do pipeline.

---

### C2 — Baseline + SAST

Adiciona uma etapa de **análise estática de código-fonte** ao pipeline baseline.

| Atributo | Detalhe |
|---|---|
| Ferramenta prevista | SonarQube |
| Categoria | SAST — *Static Application Security Testing* |
| Comparação principal | C2 − C1 |

**Objetivo:** Medir o overhead introduzido pela análise estática no lead time.

---

### C3 — C2 + SCA

Adiciona uma etapa de **análise de composição de software**, avaliando dependências e a imagem de contêiner.

| Atributo | Detalhe |
|---|---|
| Ferramenta prevista | Trivy |
| Categoria | SCA — *Software Composition Analysis* |
| Comparações principais | C3 − C2 e C3 − C1 |

**Objetivo:** Medir o overhead introduzido pela análise de dependências e camadas da imagem Docker.

---

### C4 — C3 + DAST

Adiciona uma etapa de **análise dinâmica** da aplicação em execução.

| Atributo | Detalhe |
|---|---|
| Ferramenta prevista | OWASP ZAP |
| Categoria | DAST — *Dynamic Application Security Testing* |
| Comparações principais | C4 − C3 e C4 − C1 |

**Objetivo:** Medir o overhead introduzido pela análise dinâmica de segurança, que requer a aplicação em execução.

---

### C5 — Pipeline Otimizado

Mantém todas as verificações de segurança dos cenários anteriores, aplicando estratégias para **reduzir o tempo total de execução sem remover camadas de segurança**.

**Estratégias de otimização previstas:**

- Cache de dependências
- Cache de camadas Docker
- Execução paralela de etapas independentes
- Execução condicional de etapas
- Estratégia *fail-fast*

| Atributo | Detalhe |
|---|---|
| Comparações principais | C5 − C4 e C5 − C1 |

**Objetivo:** Avaliar a viabilidade de reduzir o lead time de um pipeline DevSecOps completo por meio de otimizações técnicas.

---

## 6. 📊 Métricas Previstas

As métricas a serem coletadas em cada execução de pipeline são:

| Métrica | Descrição |
|---|---|
| Lead time total | Tempo total da execução do pipeline (início ao fim) |
| Tempo por etapa | Duração individual de cada stage do pipeline |
| Δ entre cenários | Diferença absoluta de tempo entre dois cenários |
| Overhead por ferramenta | Acréscimo de tempo atribuído a cada ferramenta de segurança |
| Ganho com otimização | Redução de tempo obtida no cenário C5 vs C4 |

> As métricas serão coletadas apenas nas etapas de implementação dos pipelines. **Nenhum dado real foi coletado até o momento.**

---

## 7. 🔍 Estratégia de Comparação

A análise comparativa será feita entre os cinco cenários, permitindo identificar:

- O **impacto individual** de cada ferramenta de segurança.
- O **impacto acumulado** ao longo dos cenários.
- O **ganho** obtido pelas otimizações no C5.

| Comparação | Pergunta respondida |
|---|---|
| C2 − C1 | Qual o overhead do SAST? |
| C3 − C2 | Qual o overhead do SCA? |
| C4 − C3 | Qual o overhead do DAST? |
| C5 − C4 | Qual o ganho das otimizações? |
| C5 − C1 | O pipeline DevSecOps otimizado é viável em relação ao baseline? |

---

## 8. 🚧 Limites desta Etapa

Esta é a **Etapa 1** do projeto, cujo objetivo é consolidar a base documental e estrutural do repositório.

Os seguintes itens **ainda não foram implementados** e serão tratados nas etapas subsequentes:

- [ ] Dockerfile final da aplicação base
- [ ] Workflows reais do GitHub Actions (C1 a C5)
- [ ] Integração com SonarQube
- [ ] Integração com Trivy
- [ ] Integração com OWASP ZAP
- [ ] Coleta real de métricas de lead time
- [ ] Deploy ou simulação de deploy em ambiente containerizado

> Este documento é uma **evidência da Etapa 1** e serve como referência arquitetural para orientar as próximas fases do TCC.