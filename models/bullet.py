from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from typing import List, Self
import os
import uuid

BULLETS_PATH = os.getenv("BULLETS_PATH", "./data/bullets")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(collection_name="bullets", embedding_function=embeddings, persist_directory=BULLETS_PATH)

class Bullet(BaseModel):
  id: uuid.UUID = Field(default_factory=uuid.uuid4)
  text: str

  def _to_document(self, experience_id: uuid.UUID) -> Document:
    return Document(page_content=self.text, metadata={"experience_id": str(experience_id)}, id=str(self.id))

  @classmethod
  def find_similar(cls, query: str, n: int = 5) -> List[Self]:
    results = store.similarity_search(query, k=n)
    return [cls(id=uuid.UUID(doc.id) if doc.id else uuid.uuid4(), text=doc.page_content) for doc in results]
  
  @classmethod
  def save_all(cls, experience_id: uuid.UUID, bullets: List[Self]):
    try:
      documents = [bullet._to_document(experience_id) for bullet in bullets]
      store.add_documents(documents)
    except Exception as e:
      print(f"Error saving bullets: {e}")

  @classmethod
  def load_by_experience(cls, experience_id: uuid.UUID) -> List[Self]:
    try:
      results = store.get(where={"experience_id": str(experience_id)})
      return [
        cls(id=uuid.UUID(id) if id else uuid.uuid4(), text=text) for id, text in zip(results["ids"], results["documents"])
      ]
    except Exception as e:
      print(f"Error loading bullets: {e}")
      return []