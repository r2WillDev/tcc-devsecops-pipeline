# 🚀 Deploy Local em Kubernetes

> **TCC:** Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD
>
> **Branch:** `feature/k8s-local-deploy`
>
> **Repositório:** [r2WillDev/tcc-devsecops-pipeline](https://github.com/r2WillDev/tcc-devsecops-pipeline)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Pré-requisitos](#-pré-requisitos)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Manifests Kubernetes](#-manifests-kubernetes)
  - [kind-cluster.yaml](#kind-clusteryaml)
  - [namespace.yaml](#namespaceyaml)
  - [deployment.yaml](#deploymentyaml)
  - [service.yaml](#serviceyaml)
- [Passo a Passo — Reprodução](#-passo-a-passo--reprodução)
- [Resultados Obtidos](#-resultados-obtidos)
- [Evidências Coletadas](#-evidências-coletadas)
- [Commits da Etapa](#-commits-da-etapa)
- [Boas Práticas Aplicadas](#-boas-práticas-aplicadas)
- [Limitações Intencionais](#-limitações-intencionais)
- [Troubleshooting](#-troubleshooting)
- [Critério de Conclusão](#-critério-de-conclusão)

---

## 🎯 Visão Geral

Esta etapa documenta o deploy local da aplicação FastAPI em um cluster Kubernetes usando **kind** (Kubernetes in Docker). O objetivo foi validar um **MVP simples, reproduzível e funcional** antes de avançar para a pipeline CI/CD e integração das ferramentas DevSecOps.

### Fluxo validado

```
localhost:8000  →  kubectl port-forward  →  Service tcc-api:80  →  Pod tcc-api:8000  →  FastAPI
```

### Endpoints verificados

| Endpoint  | Resposta esperada               |
| --------- | ------------------------------- |
| `/health` | `{"status":"ok"}`               |
| `/`       | `{"message":"TCC DevSecOps API"}` |

---

## 🛠️ Pré-requisitos

Certifique-se de que as seguintes ferramentas estão instaladas e disponíveis no `PATH` antes de iniciar.

| Ferramenta       | Finalidade                                 |
| ---------------- | ------------------------------------------ |
| Windows          | Sistema operacional                        |
| PowerShell       | Terminal para execução dos comandos        |
| VS Code          | Editor de código                           |
| Git              | Controle de versão                         |
| Docker Desktop   | Motor de containers (obrigatório para kind)|
| kind             | Criação de cluster Kubernetes local        |
| kubectl          | Gerenciamento do cluster                   |

### Verificar ferramentas instaladas

```powershell
docker version
kubectl version --client
kind version
```

---

## 📁 Estrutura de Arquivos

A estrutura de infraestrutura criada nesta etapa:

```text
infra/
├── kind/
│   └── kind-cluster.yaml       # Configuração do cluster kind
└── k8s/
    ├── namespace.yaml           # Namespace dedicado para a aplicação
    ├── deployment.yaml          # Deployment da API
    └── service.yaml             # Service para exposição interna
```

---

## 📄 Manifests Kubernetes

### `kind-cluster.yaml`

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4

nodes:
  - role: control-plane
```

**Por que apenas um `control-plane`?**
O objetivo desta etapa foi validar o deploy de forma simples e reproduzível, sem a complexidade de alta disponibilidade ou múltiplos nodes. Um único node `control-plane` é suficiente para executar a aplicação localmente, inspecionar os recursos Kubernetes e coletar as evidências necessárias para o TCC. Arquiteturas mais robustas com workers adicionais serão consideradas em etapas futuras, se necessário.

---

### `namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app
  labels:
    name: app
    purpose: application
```

**Por que um namespace dedicado?**
O namespace `app` isola os recursos da aplicação dos componentes internos do cluster (como `kube-system`). Essa separação facilita o gerenciamento, a aplicação de políticas de segurança e a limpeza de recursos sem risco de impactar o funcionamento do próprio cluster.

---

### `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tcc-api
  namespace: app
  labels:
    app: tcc-api
    tier: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tcc-api
  template:
    metadata:
      labels:
        app: tcc-api
        tier: backend
    spec:
      containers:
        - name: tcc-api
          image: tcc-devsecops-api:local
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
            timeoutSeconds: 3
            failureThreshold: 3
          resources:
            requests:
              cpu: "50m"
              memory: "64Mi"
            limits:
              cpu: "250m"
              memory: "256Mi"
```

**Explicação dos principais blocos:**

| Bloco              | Descrição                                                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `metadata`         | Identifica o Deployment com nome, namespace e labels para seleção e filtragem.                                                                  |
| `replicas`         | Define o número de instâncias do Pod. `1` é suficiente para o MVP local.                                                                        |
| `selector`         | Vincula o Deployment aos Pods com a label `app: tcc-api`. Deve ser idêntico às labels do `template`.                                            |
| `template`         | Define o template do Pod que será criado. Herda as labels que o `selector` usa para reconhecer os Pods gerenciados.                             |
| `containers`       | Lista os containers do Pod. Neste caso, apenas o container da API.                                                                              |
| `image`            | Nome e tag da imagem Docker. `tcc-devsecops-api:local` é a imagem construída localmente e carregada no kind.                                    |
| `imagePullPolicy`  | `IfNotPresent` instrui o kubelet a usar a imagem já presente no node, sem tentar baixá-la de um registry remoto. Essencial para imagens locais. |
| `containerPort`    | Informa ao Kubernetes que o container escuta na porta `8000`. Não abre a porta externamente por si só.                                          |
| `readinessProbe`   | Verifica se o Pod está pronto para receber tráfego. O Kubernetes só direciona requisições ao Pod após essa sonda retornar `HTTP 200`.            |
| `livenessProbe`    | Verifica se o Pod continua saudável durante a execução. Se falhar consecutivamente, o kubelet reinicia o container.                             |
| `resources`        | Define `requests` (mínimo garantido) e `limits` (máximo permitido) de CPU e memória. Garante que a aplicação não consuma recursos excessivos.   |

> **Por que `imagePullPolicy: IfNotPresent`?**
> O kind cria um cluster Kubernetes dentro de containers Docker. Por padrão, o kubelet tentaria baixar a imagem de um registry remoto (como o Docker Hub), o que resultaria em erro `ImagePullBackOff` para imagens locais que nunca foram publicadas. Com `IfNotPresent`, o kubelet usa a imagem carregada previamente via `kind load docker-image`, evitando esse problema.

---

### `service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tcc-api
  namespace: app
  labels:
    app: tcc-api
    tier: backend
spec:
  type: ClusterIP
  selector:
    app: tcc-api
  ports:
    - name: http
      port: 80
      targetPort: 8000
      protocol: TCP
```

**O que o Service faz?**
O Service cria um ponto de acesso fixo e estável para o Pod. Enquanto Pods podem ser recriados com IPs diferentes, o Service mantém um IP interno constante dentro do cluster. O mapeamento de portas é:

```
Service tcc-api:80  →  Pod tcc-api:8000
```

O tipo `ClusterIP` é o padrão do Kubernetes: o serviço fica acessível apenas dentro do cluster, sem exposição direta à rede externa. O acesso externo nesta etapa é feito via `kubectl port-forward`.

---

## ⚙️ Passo a Passo — Reprodução

### 1. Criar a branch

```powershell
git checkout dev
git pull origin dev
git checkout -b feature/k8s-local-deploy
```

### 2. Verificar ferramentas

```powershell
docker version
kubectl version --client
kind version
```

### 3. Criar o cluster kind

```powershell
kind create cluster --name tcc-devsecops --config .\infra\kind\kind-cluster.yaml
```

### 4. Verificar o cluster

```powershell
kubectl config current-context
kubectl get nodes
kubectl cluster-info
```

O contexto deve aparecer como `kind-tcc-devsecops` e o node deve estar em estado `Ready`.

### 5. Construir a imagem Docker

```powershell
docker build -t tcc-devsecops-api:local ./app
```

### 6. Carregar a imagem no kind

```powershell
kind load docker-image tcc-devsecops-api:local --name tcc-devsecops
```

> [!WARNING] 
> Este passo é obrigatório. O cluster kind é isolado do Docker Desktop — simplesmente construir a imagem localmente não a disponibiliza dentro do cluster. Sem este comando, o Kubernetes não encontrará a imagem e o Pod entrará em estado `ImagePullBackOff`.

### 7. Aplicar os manifests

```powershell
kubectl apply -f .\infra\k8s\namespace.yaml
kubectl apply -f .\infra\k8s\deployment.yaml
kubectl apply -f .\infra\k8s\service.yaml
```

### 8. Validar os recursos

```powershell
kubectl get all -n app
kubectl get pods -n app -o wide
kubectl get deploy -n app
kubectl get svc -n app
kubectl logs -n app deploy/tcc-api --tail=30
```

Aguarde até o Pod estar em estado `Running` e o Deployment exibir `1/1` disponível.

### 9. Fazer port-forward

```powershell
kubectl port-forward svc/tcc-api 8000:80 -n app
```

Mantenha este terminal aberto enquanto realiza os testes.

### 10. Testar a aplicação

Em **outro terminal**:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/
```

**Resultados esperados:**

```json
{"status":"ok"}
```

```json
{"message":"TCC DevSecOps API"}
```

---

## ✅ Resultados Obtidos

| Item validado       | Resultado                            |
| ------------------- | ------------------------------------ |
| Cluster kind        | Criado com sucesso                   |
| Contexto kubectl    | `kind-tcc-devsecops`                 |
| Node                | `Ready`                              |
| Namespace           | `app` criado                         |
| Deployment          | `tcc-api` com `1/1` disponível       |
| Pod                 | `Running`                            |
| Service             | `ClusterIP` na porta `80/TCP`        |
| Logs                | `/health` retornando `200 OK`        |
| Port-forward        | `localhost:8000 → svc/tcc-api:80`    |
| Endpoint `/health`  | `{"status":"ok"}`                    |
| Endpoint `/`        | `{"message":"TCC DevSecOps API"}`    |

---



## ✨ Boas Práticas Aplicadas

| Prática                                | Justificativa                                                                                    |
| -------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Cluster local com kind                 | Elimina dependência de infraestrutura em nuvem para validação local                             |
| Manifests separados por responsabilidade | Facilita leitura, manutenção e substituição individual de cada recurso                         |
| Namespace dedicado (`app`)             | Isola recursos da aplicação dos componentes internos do cluster                                  |
| Labels consistentes                    | Garante que Service, Deployment e Pods se reconheçam corretamente                               |
| Service do tipo `ClusterIP`            | Expõe o serviço apenas dentro do cluster, seguindo o princípio de menor exposição               |
| `readinessProbe`                       | Garante que o tráfego só é roteado ao Pod quando a aplicação está pronta                        |
| `livenessProbe`                        | Detecta falhas silenciosas e reinicia o container automaticamente                               |
| `requests` e `limits` de recursos      | Previne que a aplicação consuma recursos excessivos no ambiente local                           |
| Tag de imagem clara (`tcc-devsecops-api:local`) | Facilita identificação e evita ambiguidades com imagens de registries remotos          |
| Commits pequenos e descritivos         | Mantém o histórico de versão limpo e rastreável                                                 |
| Documentação de reprodução             | Permite que qualquer pessoa recrie o ambiente a partir do zero                                   |

---

## ⚠️ Limitações Intencionais

As funcionalidades abaixo **não foram implementadas nesta etapa de forma intencional**, para manter o escopo controlado e o MVP validado antes de avançar:

| Recurso omitido         | Motivo                                                                 |
| ----------------------- | ---------------------------------------------------------------------- |
| Ingress Controller      | Não necessário para validação local via port-forward                  |
| Helm                    | Adiciona complexidade desnecessária para um MVP de único serviço       |
| Banco de dados          | A API não requer persistência nesta etapa                              |
| Múltiplos microserviços | Escopo do TCC foca em um único serviço containerizado                  |
| GitHub Actions          | Será implementado nas etapas seguintes do pipeline CI/CD              |
| SonarQube / Trivy / ZAP | Ferramentas DevSecOps a serem integradas nas etapas de análise        |
| Prometheus / Grafana    | Observabilidade fora do escopo desta etapa de validação inicial       |

> [!TIP] 
>O objetivo desta etapa foi exclusivamente validar que a aplicação FastAPI pode ser implantada e acessada corretamente em um ambiente Kubernetes local. A progressão para ferramentas de segurança e observabilidade ocorrerá nas etapas seguintes do TCC.

---

## 🔧 Troubleshooting

### Docker Desktop fechado

**Sintoma:**
```
Cannot connect to the Docker daemon
```
**Solução:** Abra o Docker Desktop e aguarde até o ícone indicar que o serviço está ativo antes de executar qualquer comando.

---

### kind não encontrado

**Sintoma:**
```
kind : O termo 'kind' não é reconhecido como nome de cmdlet...
```
**Solução:** Instale o kind via [kind.sigs.k8s.io](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) e certifique-se de que o binário está no `PATH` do sistema.

---

### kubectl não encontrado

**Sintoma:**
```
kubectl : O termo 'kubectl' não é reconhecido como nome de cmdlet...
```
**Solução:** Instale o kubectl separadamente ou habilite a opção **Enable Kubernetes** no Docker Desktop (Settings → Kubernetes).

---

### ImagePullBackOff

**Causa provável:** A imagem local não foi carregada dentro do cluster kind.

**Solução:**
```powershell
kind load docker-image tcc-devsecops-api:local --name tcc-devsecops
```
Após o carregamento, delete o Pod para que ele seja recriado:
```powershell
kubectl delete pod -n app -l app=tcc-api
```

---

### CrashLoopBackOff

**Causa provável:** A aplicação iniciou e encerrou com erro logo em seguida.

**Diagnóstico:**
```powershell
kubectl logs -n app deploy/tcc-api
kubectl describe pod -n app -l app=tcc-api
```
Verifique os logs para identificar a causa do crash (erro de importação, porta incorreta, variável de ambiente ausente etc.).

---

### Porta 8000 já está em uso

**Sintoma:** O port-forward falha porque a porta local `8000` está ocupada por outro processo.

**Solução:** Use uma porta alternativa:
```powershell
kubectl port-forward svc/tcc-api 8080:80 -n app
curl.exe http://localhost:8080/health
```

---

### Service não encontra o Pod

**Causa provável:** O campo `selector` do Service não corresponde exatamente às labels do Deployment.

**Diagnóstico:**
```powershell
kubectl get endpoints -n app
```
Se o endpoint aparecer vazio (`<none>`), compare as labels do Service com as labels dos Pods:
```powershell
kubectl get pods -n app --show-labels
kubectl describe svc tcc-api -n app
```

---

### ReadinessProbe falhando

**Causa provável:** O endpoint `/health` não está disponível ou a aplicação não está escutando em `0.0.0.0:8000`.

**Diagnóstico:**
```powershell
kubectl describe pod -n app -l app=tcc-api
kubectl logs -n app deploy/tcc-api
```
Verifique se o Uvicorn está sendo iniciado com o parâmetro `--host 0.0.0.0` no Dockerfile:
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```



---

<div align="center">



A aplicação FastAPI está operacional em Kubernetes local.
A próxima etapa integrará ferramentas DevSecOps (SAST, DAST, SCA) ao pipeline CI/CD.



*TCC — Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD*

</div>