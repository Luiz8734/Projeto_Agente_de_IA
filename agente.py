import os 
from dotenv import load_dotenv
from rich import print
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from indexar import embeddings
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_core.messages import HumanMessage,SystemMessage

from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

vectorstrore = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
retriver = vectorstrore.as_retriever(search_kwargs={"k":4})
llm = ChatGroq(model=os.getenv("GROQ_MODEL"), temperature=0)     
prompt = ChatPromptTemplate.from_template(
    "Voce é um assitente de uma loja de eletronicos LMSTECH. Responda de forma educada"
    "Contexto: {context}\nPergunta:{question}"
)

def format_chunks(chunks):
    return"\n\n".join(chunk.page_content  for chunk in chunks)

@tool
def buscar_rag(query: str) -> str:
    """
    Busca de inforamações da Loja de eletronicos, como:
    descrição, endereço,produto,politicas,fidelidade, e duvidas frequentes
    """
    chunks = retriver.invoke(query)
    return format_chunks(chunks)
class Estado(TypedDict):
    messages: Annotated[list, add_messages]

def chamar_llm(estado: Estado) -> Estado:
    return {"messages": [llm.invoke(estado["messages"])]}

ferramentas = [buscar_rag]

llm_com_ferramentas = llm.bind_tools(ferramentas)

def chamar_llm_com_ferramentas(estado: Estado) -> Estado:
    return {"messages": [llm_com_ferramentas.invoke(estado["messages"])]}

builder =  StateGraph(Estado)
builder.add_node("no_llm", chamar_llm_com_ferramentas)
builder.add_node("tools", ToolNode(ferramentas))

builder.add_edge(START, "no_llm")
builder.add_conditional_edges("no_llm",tools_condition )
builder.add_edge("tools", "no_llm")
builder.add_edge("no_llm", END)

graph=builder.compile()
# Gera uma imagem PNG usando o serviço online do Mermaid (não requer pygraphviz)
img_data = graph.get_graph().draw_mermaid_png(
    draw_method=MermaidDrawMethod.API
)

with open("graph.png", "wb") as f:
    f.write(img_data)

estado_global = Estado({"messages": [
    SystemMessage(content="Você é um assistente da loja LMSTECH. Responda de forma educada.")
]})

def chamar_grafo(texto):
    global estado_global
    estado_global ["messages"].append(HumanMessage(content=texto))
    estado_global= graph.invoke(estado_global)
    return estado_global["messages"][-1].content

if __name__ == "__main__":
    print("ok")
    print(chamar_grafo("Meu nome é luiz"))
    print(chamar_grafo("quais produtos tem?"))
    print(chamar_grafo("qual é meu nome ?"))