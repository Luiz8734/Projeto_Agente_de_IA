# 🤖 Agente de IA — LMSTECH

Agente conversacional inteligente para atendimento ao cliente de uma loja de eletrônicos fictícia chamada **LMSTECH**. O agente responde perguntas sobre produtos, políticas da loja e saldo de pontos do programa de fidelidade usando **RAG (Retrieval-Augmented Generation)** com documentos PDF e um banco de dados de clientes em JSON.

---

## 📁 Estrutura do Projeto

```
Projeto_Agente_de_IA-main/
├── agente.py          # Agente principal com grafo LangGraph
├── agente2.py         # Agente alternativo usando create_agent (LangChain)
├── indexar.py         # Script para indexar documentos PDF no FAISS
├── main.py            # Entrypoint padrão do projeto
├── clientes.json      # Base de dados de clientes e saldo de pontos
├── langgraph.json     # Configuração para deploy via LangGraph CLI
├── pyproject.toml     # Dependências e metadados do projeto
├── graph.png          # Imagem gerada do grafo de estados (gerada automaticamente)
├── docs/
│   └── LMStech1.pdf   # Documento com informações da loja (indexado no RAG)
└── vectorstore/
    ├── index.faiss    # Índice vetorial FAISS (gerado pelo indexar.py)
    └── index.pkl      # Mapeamento dos chunks (gerado pelo indexar.py)
```

---

## 🧠 Como Funciona

### Visão geral da arquitetura

```
Usuário
   ↓
[HumanMessage]
   ↓
[Nó LLM — ChatGroq]
   ↓ (decide se precisa de ferramenta)
   ├─→ [Nó Tools] ──→ buscar_rag(query)           → FAISS / PDF
   │                └→ buscar_saldo_por_nome(nome) → clientes.json
   │       ↓
   └──────[Nó LLM novamente com resultado]
              ↓
         [Resposta final]
```

O projeto usa **LangGraph** para orquestrar um grafo de estados com dois nós principais:

- **`no_llm`**: invoca o modelo de linguagem (Groq) com as ferramentas disponíveis ligadas a ele.
- **`tools`**: executa a ferramenta solicitada pelo LLM e retorna o resultado para o grafo.

O LLM decide automaticamente quando usar cada ferramenta com base na pergunta do usuário.

---

### 🔧 Ferramentas disponíveis

#### `buscar_rag(query: str)`
Realiza uma busca semântica no **índice vetorial FAISS** gerado a partir dos PDFs da pasta `docs/`. Retorna os 4 trechos mais relevantes para a pergunta. Usada para responder perguntas sobre:
- Produtos disponíveis
- Endereço e informações da loja
- Políticas de troca e devolução
- Programa de fidelidade (regras gerais)
- Dúvidas frequentes

#### `buscar_saldo_por_nome(parte_nome: str)`
Busca no arquivo `clientes.json` pelo nome (ou parte do nome) do cliente, de forma **case-insensitive**. Retorna o nome completo, número de cadastro e saldo de pontos. Usada quando o usuário pergunta quantos pontos tem.

---

### 🗂️ RAG — Indexação dos Documentos

O módulo `indexar.py` é responsável por carregar os PDFs da pasta `docs/`, dividir em chunks e indexar no FAISS:

1. Carrega todos os arquivos `.pdf` recursivamente da pasta `docs/`
2. Divide os documentos em chunks de **300 caracteres** com **overlap de 50**
3. Gera embeddings usando o modelo multilíngue `intfloat/multilingual-e5-small` (HuggingFace)
4. Salva o índice na pasta `vectorstore/`

> O vectorstore já está pré-gerado no repositório. Só é necessário re-indexar se os PDFs forem alterados.

---

### 💾 Base de Clientes

O arquivo `clientes.json` contém uma lista de clientes com os campos:

```json
{
  "nome": "Luiz Morais",
  "numeroCadastro": "C012",
  "saldoPontos": 1980
}
```

A busca é feita por substring do nome, sem distinção de maiúsculas/minúsculas.

---

## ⚙️ Pré-requisitos

- Python **3.13+**
- [`uv`](https://docs.astral.sh/uv/) (gerenciador de pacotes recomendado) **ou** `pip`
- Conta no [Groq](https://console.groq.com/) para obter a API Key
- *(Opcional)* [LangGraph CLI](https://langchain-ai.github.io/langgraph/cloud/reference/cli/) para deploy como API

---

## 🚀 Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/Projeto_Agente_de_IA.git
cd Projeto_Agente_de_IA
```

### 2. Crie o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com as variáveis de ambiente necessárias:

```env
GROQ_API_KEY=sua_chave_api_do_groq
GROQ_MODEL=llama-3.1-8b-instant
```

> Para obter sua chave: acesse [https://console.groq.com/keys](https://console.groq.com/keys)
>
> Modelos disponíveis no Groq: `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, `gemma2-9b-it`, entre outros.

### 3. Instale as dependências

**Com `uv` (recomendado):**
```bash
uv sync
```

**Com `pip`:**
```bash
pip install -e .
```

### 4. (Opcional) Re-indexe os documentos

Só execute este passo se quiser adicionar novos PDFs à pasta `docs/` ou se o vectorstore não existir:

```bash
# Com uv
uv run python indexar.py

# Com pip
python indexar.py
```

### 5. Execute o agente

```bash
# Com uv
uv run python agente.py

# Com pip
python agente.py
```

A execução de `agente.py` como `__main__` roda uma sequência de testes demonstrando memória conversacional:

```
✅ "Meu nome é luiz"
✅ "quais produtos tem?"
✅ "qual é meu nome?"
✅ "quantos pontos eu tenho?"
```

---

## 🌐 Deploy como API com LangGraph CLI

O arquivo `langgraph.json` configura o deploy do agente como uma API REST usando o LangGraph Platform:

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./agente2.py:agent"
  },
  "env": ".env"
}
```

Para subir a API localmente:

```bash
# Instale o CLI (já incluso nas dependências)
pip install langgraph-cli

# Suba o servidor
langgraph dev
```

A API ficará disponível em `http://localhost:2024` com interface gráfica de testes no LangGraph Studio.

---

## 📂 Adicionando Novos Documentos

Para adicionar informações ao conhecimento do agente:

1. Coloque o arquivo `.pdf` na pasta `docs/`
2. Execute a re-indexação:
   ```bash
   python indexar.py
   ```
3. O novo conteúdo já estará disponível para consulta via `buscar_rag`

---

## 🗺️ Grafo de Estados

Ao executar `agente.py`, o arquivo `graph.png` é gerado automaticamente na raiz do projeto com a visualização do grafo de estados usando o serviço Mermaid online.

```
START → no_llm → tools → no_llm → END
                    ↑ (condicional: só vai para tools se o LLM chamar uma ferramenta)
```

---

## 📦 Dependências Principais

| Pacote | Função |
|---|---|
| `langchain-groq` | Integração com modelos Groq (LLM) |
| `langchain-community` | FAISS, PyPDFLoader |
| `langchain-huggingface` | Embeddings locais (HuggingFace) |
| `langgraph` | Orquestração do grafo de estados |
| `faiss-cpu` | Busca vetorial para RAG |
| `sentence-transformers` | Modelos de embeddings |
| `pypdf` | Leitura de PDFs |
| `python-dotenv` | Carregamento do `.env` |
| `rich` | Output formatado no terminal |

---

## ⚠️ Observações

- O arquivo `agente2.py` é uma variante experimental que usa `create_agent` do LangChain com suporte a **memória persistente** via `MemorySaver`. Ele está configurado para ser exposto pelo LangGraph CLI, mas o checkpointer está comentado na versão atual.
- O `main.py` é apenas o entrypoint padrão gerado pelo `uv` e não contém lógica do agente.
- Os arquivos `.langgraph_api/*.pckl` são checkpoints gerados pelo servidor LangGraph e não precisam ser commitados (já no `.gitignore` recomendado).