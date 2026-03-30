import os 
from dotenv import load_dotenv
from rich import print
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from indexar import embeddings
from langchain_core.tools import tool

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
    chunks = retriver.invoke(query)
    return format_chunks(chunks)

def chamar_llm(texto):
    chain = {"context": buscar_rag, "question": RunnablePassthrough()} | prompt | llm
    resultado = chain.invoke(texto)
    return resultado.content

if __name__ == "__main__":
    print(chamar_llm("Quais produtos tem?"))