# 🔐 Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD

> Trabalho de Conclusão de Curso — Ciência da Computação

---

## 📌 Sobre o Projeto

Este repositório é o artefato principal de um Trabalho de Conclusão de Curso que investiga, de forma experimental, como a integração de ferramentas de segurança em pipelines CI/CD afeta o **lead time** — o tempo total entre o início de uma execução e a conclusão do deploy.

**Problema de pesquisa:**
> Como a integração de ferramentas de análise de segurança — SAST, DAST e SCA — afeta o lead time em pipelines CI/CD, e como otimizar esse impacto?

**Objetivo geral:**
Desenvolver e avaliar um pipeline DevSecOps otimizado para minimizar o impacto no tempo de deploy de uma aplicação containerizada, sem abrir mão das práticas de segurança.

---

## 🗂️ Estrutura do Repositório

```text
tcc-devsecops-pipeline/
├── app/          # Aplicação base utilizada nos experimentos
├── ci/           # Definições e documentação dos pipelines CI/CD
├── docs/         # Documentação técnica e acadêmica do TCC
├── infra/        # Arquivos de infraestrutura do ambiente experimental
├── analysis/     # Dados, métricas coletadas e análises dos experimentos
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🧪 Cenários Experimentais

O experimento é estruturado em cinco cenários progressivos. Cada cenário adiciona ou otimiza uma camada do pipeline, permitindo isolar e mensurar o impacto de cada ferramenta no lead time.

| Cenário | Nome | Descrição |
|---|---|---|
| **C1** | Baseline | Pipeline sem ferramentas de segurança. Referência de tempo base. |
| **C2** | Baseline + SAST | Adiciona análise estática de código (SonarQube). |
| **C3** | C2 + SCA | Adiciona análise de dependências e imagem de contêiner (Trivy). |
| **C4** | C3 + DAST | Adiciona análise dinâmica da aplicação em execução (OWASP ZAP). |
| **C5** | Pipeline Otimizado | Mantém todas as verificações de segurança com estratégias de otimização. |

### C1 — Pipeline Baseline
Pipeline inicial, sem qualquer ferramenta de segurança integrada. Serve como ponto de referência para todas as comparações subsequentes.
- **Objetivo:** medir o tempo base de execução do pipeline.

### C2 — Baseline + SAST
Incorpora análise estática de código-fonte ao pipeline.
- **Ferramenta prevista:** SonarQube
- **Objetivo:** medir o impacto da análise estática no lead time.

### C3 — C2 + SCA
Adiciona análise de composição de software, cobrindo dependências de projeto e a imagem de contêiner gerada.
- **Ferramenta prevista:** Trivy
- **Objetivo:** medir o impacto acumulado do SCA no lead time.

### C4 — C3 + DAST
Incorpora análise dinâmica sobre a aplicação em execução, simulando ataques para identificar vulnerabilidades em tempo de execução.
- **Ferramenta prevista:** OWASP ZAP
- **Objetivo:** medir o impacto acumulado do DAST no lead time.

### C5 — Pipeline Otimizado
Mantém todas as verificações de segurança dos cenários anteriores, aplicando estratégias de otimização para reduzir o lead time total.
- **Estratégias previstas:**
  - Cache de dependências
  - Cache de camadas Docker
  - Paralelismo entre etapas independentes
  - Execução condicional de etapas
  - Estratégia *fail-fast*
- **Objetivo:** avaliar se é possível reduzir o lead time mantendo cobertura completa de segurança.

---

## 🛠️ Ferramentas Previstas

As ferramentas listadas abaixo serão integradas progressivamente ao longo das etapas do projeto. **Nenhuma delas está implementada na etapa atual.**

| Categoria | Ferramenta | Finalidade |
|---|---|---|
| Controle de versão | Git / GitHub | Versionamento e hospedagem do código |
| CI/CD | GitHub Actions | Automação dos pipelines experimentais |
| Aplicação | FastAPI | Aplicação base para os experimentos |
| Containerização | Docker | Empacotamento e execução da aplicação |
| SAST | SonarQube | Análise estática do código-fonte |
| SCA | Trivy | Análise de dependências e imagem de contêiner |
| DAST | OWASP ZAP | Análise dinâmica da aplicação em execução |

---

## 📐 Como o Experimento Será Conduzido

1. **Definição da aplicação base:** uma API simples em FastAPI será desenvolvida como objeto de estudo, sem lógica de negócio complexa, focada em viabilizar os experimentos.
2. **Implementação dos cenários:** cada cenário (C1 a C5) será implementado como um workflow independente no GitHub Actions.
3. **Coleta de dados:** para cada cenário, o pipeline será executado múltiplas vezes. O lead time de cada etapa e do pipeline completo será registrado.
4. **Análise comparativa:** os dados coletados serão analisados para quantificar o impacto de cada ferramenta e a efetividade das otimizações aplicadas no C5.
5. **Documentação dos resultados:** os dados brutos, análises e conclusões serão registrados no diretório `analysis/` e consolidados na documentação acadêmica em `docs/`.

---

## 📊 Métricas Previstas

As seguintes métricas serão coletadas e analisadas em cada cenário experimental:

- **Lead time total do pipeline** — tempo total de execução do início ao fim.
- **Tempo por etapa** — duração individual de cada job/step.
- **Overhead de segurança** — diferença de tempo em relação ao C1 (baseline).
- **Taxa de redução no C5** — comparação entre o C4 (completo sem otimização) e o C5 (otimizado).
- **Número de execuções por cenário** — para controle estatístico mínimo dos resultados.

---

## 📚 Documentação

A documentação do projeto está organizada no diretório `docs/` e será expandida ao longo das etapas do TCC. Inclui:

- Referencial teórico e decisões de design
- Especificação dos cenários experimentais
- Protocolos de coleta de dados
- Relatórios de resultados e análises

---

## 📍 Estado Atual do Projeto

**Etapa atual:** `Consolidar base do projeto`

O repositório encontra-se na fase inicial de organização. O foco desta etapa é estabelecer a estrutura de diretórios, definir a documentação base e preparar o repositório para as implementações futuras.

**O que já foi feito:**
- [x] Definição da estrutura de diretórios do repositório
- [x] Documentação inicial do projeto (este README)
- [x] Definição dos cenários experimentais
- [x] Aplicação base em FastAPI
- [x] Containerização com Docker

**O que ainda não foi implementado:**
- [ ] Workflows do GitHub Actions
- [ ] Integração com SonarQube, Trivy e OWASP ZAP
- [ ] Infraestrutura experimental

---

## 🚀 Próximos Passos

- [ ] Implementar o pipeline C1 (baseline) no GitHub Actions
- [ ] Validar a coleta de métricas de lead time
- [ ] Implementar progressivamente os cenários C2, C3 e C4
- [ ] Implementar e avaliar o cenário C5 com as otimizações

---

## 📄 Licença

Este projeto está licenciado sob os termos da licença [MIT](./LICENSE).

---

<p align="center">
  Trabalho de Conclusão de Curso — Ciência da Computação<br/>
  Desenvolvido para fins de pesquisa acadêmica
</p>
