from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma(collection_name="experience", embedding_function=embeddings, persist_directory="./chroma")

