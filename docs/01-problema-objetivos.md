# 📄 Problema e Objetivos

> **Documento:** `docs/01-problema-objetivos.md`
> **Projeto:** TCC — Ciência da Computação
> **Etapa atual:** Etapa 1 — Consolidar base do projeto
> **Status:** Base conceitual documentada *(implementação dos pipelines pendente)*

---

## 1. Tema do Trabalho

**Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD**

Este trabalho investiga de forma experimental como a incorporação de ferramentas de análise de segurança — SAST, DAST e SCA — afeta o tempo total de execução (lead time) de pipelines de integração e entrega contínua (CI/CD), e propõe estratégias de otimização para minimizar esse impacto.

---

## 2. Contexto

A cultura DevSecOps propõe integrar práticas de segurança diretamente no ciclo de desenvolvimento de software, em vez de tratá-las como uma etapa isolada ao final do processo. Em ambientes que utilizam pipelines CI/CD, essa integração representa um desafio: cada ferramenta de segurança adicionada ao pipeline tende a aumentar o tempo de execução, impactando diretamente a velocidade de entrega.

Este TCC utiliza como base uma aplicação containerizada simples, desenvolvida com **FastAPI** e **Docker**, executada em um repositório **GitHub** com pipelines automatizados via **GitHub Actions**. O projeto estrutura experimentos comparativos entre diferentes configurações de pipeline, variando a presença e a combinação de ferramentas de segurança.

---

## 3. Problema de Pesquisa

> *Como a integração de ferramentas de análise de segurança — SAST, DAST e SCA — afeta o lead time em pipelines CI/CD, e como é possível otimizar esse impacto?*

O problema central está na tensão entre **segurança** e **velocidade de entrega**. Pipelines sem controles de segurança são rápidos, mas arriscados. Pipelines com múltiplas análises de segurança tendem a ser mais lentos, o que pode desestimular sua adoção em times que priorizam velocidade.

---

## 4. Justificativa

A adoção de DevSecOps cresce continuamente na indústria, mas poucos estudos quantificam de forma experimental e controlada o custo de desempenho associado à inclusão de cada categoria de ferramenta de segurança em pipelines CI/CD reais. Este trabalho busca preencher essa lacuna ao:

- Medir objetivamente o lead time em cenários com e sem ferramentas de segurança;
- Identificar quais ferramentas impactam mais o tempo de pipeline;
- Avaliar técnicas de otimização (cache, paralelismo, execução condicional, fail-fast) para reduzir esse impacto sem abrir mão da segurança.

---

## 5. Objetivo Geral

Desenvolver e avaliar um pipeline DevSecOps otimizado, com o propósito de minimizar o impacto no lead time de deploy de uma aplicação containerizada, mantendo cobertura de segurança nas dimensões SAST, SCA e DAST.

---

## 6. Objetivos Específicos

1. **Revisar** a literatura sobre DevSecOps, CI/CD e métricas de desempenho de pipelines.
2. **Desenvolver** uma aplicação base simples com FastAPI e Docker, adequada para uso como objeto de experimentação.
3. **Implementar** pipelines CI/CD com GitHub Actions representando cinco cenários experimentais distintos (C1 a C5).
4. **Integrar** ferramentas de segurança ao pipeline: SonarQube (SAST), Trivy (SCA) e OWASP ZAP (DAST).
5. **Medir** o lead time de cada cenário por meio de execuções repetidas e controladas.
6. **Analisar** estatisticamente os dados coletados para identificar o impacto individual e acumulado de cada ferramenta.
7. **Propor e validar** um pipeline otimizado (C5) que aplique técnicas para reduzir o overhead introduzido pelas ferramentas de segurança.

---

## 7. Delimitação do Escopo

Este trabalho delimita-se aos seguintes aspectos:

| Inclui | Não inclui |
|---|---|
| Pipelines executados via GitHub Actions | Plataformas de CI/CD alternativas (Jenkins, GitLab CI, etc.) |
| Aplicação backend simples com FastAPI | Aplicações de alta complexidade ou sistemas legados |
| Containerização com Docker | Orquestração com Kubernetes ou ambientes de produção real |
| Análise de lead time como métrica principal | Análise de qualidade de código ou cobertura de vulnerabilidades encontradas |
| Ferramentas: SonarQube, Trivy, OWASP ZAP | Outras ferramentas de segurança além das previstas |
| Ambiente experimental e controlado | Ambientes de produção ou multi-ambiente |

---

## 8. Relação com os Cenários Experimentais (C1–C5)

Os experimentos serão estruturados em cinco cenários progressivos, conforme descrito a seguir. Cada cenário adiciona ou otimiza elementos em relação ao anterior, permitindo isolar o impacto de cada ferramenta.

| Cenário | Descrição | Ferramentas de Segurança |
|---|---|---|
| **C1** | Pipeline baseline — apenas build, test e deploy | Nenhuma |
| **C2** | C1 + análise estática de código (SAST) | SonarQube |
| **C3** | C2 + análise de dependências e imagem (SCA) | SonarQube + Trivy |
| **C4** | C3 + análise dinâmica da aplicação em execução (DAST) | SonarQube + Trivy + OWASP ZAP |
| **C5** | Pipeline otimizado com cache, paralelismo, execução condicional e fail-fast | SonarQube + Trivy + OWASP ZAP |

> [!NOTE] 
> Os cenários C1 a C5 ainda **não foram implementados** nesta etapa. A implementação dos pipelines está prevista para etapas futuras do projeto.

---

## 9. Resultado Esperado

Ao final do trabalho, espera-se obter:

- **Dados quantitativos** sobre o lead time de cada cenário experimental;
- **Análise comparativa** do impacto de SAST, SCA e DAST no tempo de pipeline;
- **Um pipeline otimizado** (C5) com overhead reduzido em relação ao C4, mantendo cobertura de segurança equivalente;
- **Diretrizes práticas** para equipes que desejam adotar DevSecOps sem comprometer significativamente a velocidade de entrega.

---

## 10. Observação sobre a Etapa Atual

> 📌 Este documento faz parte da **Etapa 1 — Consolidar base do projeto**.

Nesta etapa, o objetivo é exclusivamente **organizar e documentar a base conceitual e estrutural do repositório**. Não estão previstas, para esta etapa, as seguintes atividades:

- Implementação de Dockerfiles ou containerização da aplicação;
- Configuração de workflows no GitHub Actions;
- Integração de SonarQube, Trivy ou OWASP ZAP;
- Execução dos experimentos ou coleta de dados.

Este arquivo serve como **evidência documental da Etapa 1**, registrando o problema de pesquisa, os objetivos e o escopo do trabalho antes do início da implementação técnica.

---

*Documento gerado na Etapa 1 do TCC. Sujeito a revisões nas etapas subsequentes.*