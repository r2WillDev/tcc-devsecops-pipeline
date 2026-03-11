# Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD

<div align="center">

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)
![TCC](https://img.shields.io/badge/TCC-Ciência%20da%20Computação-blue?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerização-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orquestração-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![SonarQube](https://img.shields.io/badge/SonarQube-SAST-4E9BCD?style=for-the-badge&logo=sonarqube&logoColor=white)
![OWASP](https://img.shields.io/badge/OWASP%20ZAP-DAST-000000?style=for-the-badge&logo=owasp&logoColor=white)
![Trivy](https://img.shields.io/badge/Trivy-SCA-1904DA?style=for-the-badge&logo=aquasecurity&logoColor=white)

**Trabalho de Conclusão de Curso — Bacharelado em Ciência da Computação**

</div>

---

## Resumo / Abstract

**PT-BR:** Este trabalho investiga, por meio de uma abordagem experimental quantitativa, o impacto da integração de ferramentas de segurança — análise estática (SAST), análise de composição de software (SCA) e análise dinâmica (DAST) — no *lead time* de pipelines de Integração e Entrega Contínua (CI/CD). A partir da construção e instrumentação de cenários controlados sobre um microsserviço containerizado, o estudo busca mensurar o custo temporal associado ao paradigma *shift-left security* e propor estratégias de otimização capazes de conciliar agilidade e segurança no ciclo de vida de desenvolvimento de software.

**EN:** This work investigates, through a quantitative experimental approach, the impact of integrating security tooling — Static Application Security Testing (SAST), Software Composition Analysis (SCA), and Dynamic Application Security Testing (DAST) — on the lead time of Continuous Integration and Continuous Delivery (CI/CD) pipelines. By constructing and instrumenting controlled scenarios over a containerized microservice, the study aims to measure the temporal cost associated with the *shift-left security* paradigm and to propose optimization strategies capable of reconciling agility and security throughout the software development lifecycle.

---

## Motivação e Justificativa

O movimento **DevSecOps** representa uma evolução cultural e técnica sobre o modelo DevOps tradicional, ao incorporar a segurança como uma responsabilidade compartilhada e contínua ao longo de todo o ciclo de vida do desenvolvimento de software (SDLC). Em contraste com abordagens reativas — nas quais auditorias e testes de segurança ocorrem apenas em fases finais — o princípio de ***shift-left security*** preconiza que controles e verificações de segurança devem ser antecipados para as etapas mais iniciais do pipeline.

> *"Security is not a feature to be added; it is a property to be designed in."* — adaptado de Ross Anderson, *Security Engineering* (2020).

Contudo, essa antecipação não é isenta de custos. A adição de estágios de análise estática, varredura de dependências e testes dinâmicos a um pipeline já existente impõe uma sobrecarga mensurável no **lead time** — o intervalo temporal entre o *commit* de uma alteração e sua disponibilização em produção. Em ambientes de entrega contínua de alta cadência, essa latência adicional pode se tornar um gargalo operacional relevante, afetando a produtividade das equipes de engenharia e a competitividade do negócio.

A lacuna identificada na literatura reside na **escassez de estudos experimentais controlados** que quantifiquem esse impacto de forma isolada por categoria de ferramenta e que proponham estratégias de otimização validadas empiricamente. A maioria dos trabalhos disponíveis aborda a adoção de DevSecOps sob perspectivas qualitativas ou de maturidade organizacional, sem fornecer dados experimentais precisos sobre o custo temporal de cada camada de segurança inserida no pipeline.

Este trabalho posiciona-se, portanto, na interseção entre **engenharia de software experimental**, **segurança de aplicações** e **engenharia de confiabilidade de sites (SRE)**, contribuindo com evidências empíricas que possam fundamentar decisões de *pipeline design* em contextos industriais e acadêmicos.

---

## Objetivos

### Objetivo Geral

Desenvolver, instrumentar e avaliar um pipeline DevSecOps otimizado para minimizar o impacto no tempo de *deploy* de uma aplicação containerizada, fornecendo evidências empíricas sobre o custo-benefício de cada camada de segurança integrada ao processo de CI/CD.

### Objetivos Específicos

- **OE1:** Revisar sistematicamente a literatura sobre DevSecOps, *shift-left security* e métricas de performance em pipelines CI/CD, delimitando o estado da arte sobre o impacto de ferramentas de segurança no *lead time*.
- **OE2:** Projetar e implementar um microsserviço-referência containerizado, adequado ao papel de *system under test* (SUT) nos experimentos.
- **OE3:** Construir cenários de pipeline progressivos e controlados no GitHub Actions, integrando incrementalmente ferramentas de SAST (SonarQube), SCA (Trivy) e DAST (OWASP ZAP).
- **OE4:** Instrumentar a coleta automatizada de métricas de execução via API do GitHub Actions, garantindo reprodutibilidade e rigor estatístico nas medições.
- **OE5:** Analisar quantitativamente os dados coletados, identificando os estágios de maior impacto e os ganhos proporcionados pelas estratégias de otimização.
- **OE6:** Propor e validar um conjunto de boas práticas e padrões de otimização de pipeline DevSecOps, sistematizados como recomendações aplicáveis a contextos similares.

---

## Desenho Experimental

O núcleo metodológico deste trabalho é uma **pesquisa experimental quantitativa** estruturada em cinco cenários de pipeline (*C1* a *C5*), construídos sobre uma arquitetura de microsserviço containerizado. Cada cenário representa uma configuração distinta do pipeline de CI/CD, permitindo o isolamento e a mensuração do impacto de cada camada de segurança adicionada.

A variável dependente principal é o **lead time de pipeline** — mensurado em segundos, do gatilho do *workflow* até a conclusão do estágio de *deploy* — coletado por meio da API REST do GitHub Actions em múltiplas execuções por cenário, de modo a permitir análise estatística com controle de variância.

```
┌──────────────────────────────────────────────────────────────────┐
│              PROGRESSÃO DOS CENÁRIOS EXPERIMENTAIS               │
│                                                                  │
│  C1  →  Build + Testes Unitários + Deploy  (Baseline)            │
│  C2  →  C1 + SAST (SonarQube)                                    │
│  C3  →  C2 + SCA  (Trivy)                                        │
│  C4  →  C3 + DAST (OWASP ZAP — Amostrado)                        │
│  C5  →  Pipeline Otimizado (Paralelismo + Fail-Fast + Cache)     │
└──────────────────────────────────────────────────────────────────┘
```

### C1 — Baseline

| Atributo | Descrição |
|---|---|
| **Composição** | Build da imagem Docker → Execução de testes unitários → Deploy |
| **Objetivo** | Estabelecer o tempo de referência (*baseline*) de um pipeline sem controles de segurança ativos |
| **Métricas** | Lead time total, tempo por estágio |
| **Ferramentas** | GitHub Actions, Docker |

O cenário *C1* representa o estado mínimo viável de um pipeline de entrega contínua, sem nenhuma instrumentação de segurança. Serve como **ponto zero** para o cálculo do *overhead* relativo introduzido pelos cenários subsequentes.

---

### C2 — Baseline + SAST

| Atributo | Descrição |
|---|---|
| **Composição** | C1 + Análise Estática de Segurança de Aplicação |
| **Ferramenta** | SonarQube (modo Quality Gate) |
| **Objetivo** | Mensurar o impacto da análise estática de código-fonte no lead time |
| **Variável isolada** | Custo temporal do estágio de SAST |

O **SAST** (*Static Application Security Testing*) analisa o código-fonte em busca de vulnerabilidades conhecidas sem executar a aplicação. O SonarQube será configurado com um *Quality Gate* padrão, bloqueando o pipeline em caso de falhas críticas.

---

### C3 — C2 + SCA

| Atributo | Descrição |
|---|---|
| **Composição** | C2 + Análise de Composição de Software |
| **Ferramenta** | Trivy (varredura de imagem de contêiner e dependências) |
| **Objetivo** | Mensurar o impacto cumulativo da varredura de vulnerabilidades em dependências e camadas da imagem Docker |
| **Variável isolada** | Custo temporal do estágio de SCA |

O **SCA** (*Software Composition Analysis*) examina as dependências de terceiros e as camadas da imagem de contêiner, mapeando CVEs (*Common Vulnerabilities and Exposures*) conhecidos. O Trivy será configurado para falhar o pipeline em vulnerabilidades de severidade *CRITICAL* ou *HIGH*.

---

### C4 — C3 + DAST (Amostrado)

| Atributo | Descrição |
|---|---|
| **Composição** | C3 + Análise Dinâmica de Segurança de Aplicação |
| **Ferramenta** | OWASP ZAP (modo *baseline scan*) |
| **Objetivo** | Mensurar o impacto do teste dinâmico sobre uma instância em execução da aplicação |
| **Variável isolada** | Custo temporal do estágio de DAST |
| **Observação** | O ZAP será executado em modo amostrado (*baseline*) para controle do tempo de varredura |

O **DAST** (*Dynamic Application Security Testing*) testa a aplicação em tempo de execução, simulando ataques externos. Por sua natureza, é o estágio de maior latência esperada. A escolha do modo *baseline scan* do OWASP ZAP visa equilibrar cobertura de teste e controle do tempo de execução.

---

### C5 — Pipeline Otimizado

| Atributo | Descrição |
|---|---|
| **Composição** | Todos os estágios de C4, reestruturados com estratégias de otimização |
| **Objetivo** | Validar se estratégias de engenharia de pipeline reduzem o lead time sem comprometer a cobertura de segurança |
| **Estratégias aplicadas** | Paralelismo de *jobs*, política *fail-fast*, cache de dependências e camadas Docker, execução condicional de estágios |

> Este cenário representa a **proposta central de contribuição** do trabalho: um modelo de pipeline DevSecOps que incorpora segurança completa (*C4*) com desempenho otimizado em relação ao *baseline* de segurança. O ganho relativo de *C5* sobre *C4* será a principal métrica de avaliação da eficácia das otimizações propostas.

---

<div align="center">

*Este repositório é parte de um Trabalho de Conclusão de Curso e encontra-se em desenvolvimento ativo.*

</div>

## Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes.

---

## Autor

**Arthur Willyams Dantas Soares**
Trabalho de Conclusão de Curso — Ciência da Computação

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/arthur-willyams-938659247/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/r2WillDev)

> *Orientador(a): Adilson da Silva — Faculdade Nova Roma *
