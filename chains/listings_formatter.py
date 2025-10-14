from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from chains.misc import to_dict, flatten

class Listing(BaseModel):
  title: str = Field(description="The title displayed in the listing")
  company: str = Field(description="The company offering the position")
  posted_date: Optional[date] = Field(default=None, description="When the listing was posted")
  description: str = Field(description="A summarized description of the position's responsibilities")
  keywords: List[str] = Field(default_factory=list, description="A list of relevant keywords, required skills and tools mentioned in the listing")

prompt = ChatPromptTemplate.from_template("""
Extract job listing information from the text below.
Return valid JSON that matches the Listing schema.

Text:
{content}
""")

model = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(Listing)
listings_formatter = RunnablePassthrough.assign(_formatted=prompt | model | to_dict) | flatten(("_formatted",)) | RunnablePassthrough.assign(keywords=lambda input: sorted(input["keywords"]))
