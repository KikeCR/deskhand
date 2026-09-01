"""CrewAI tool that lets the Research Agent query the company-docs vectorstore."""

from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from rag.retriever import query as rag_query


class RAGSearchInput(BaseModel):
    query: str = Field(
        ..., description="A specific, natural-language question about company policy."
    )


class RAGSearchTool(BaseTool):
    name: str = "search_company_docs"
    description: str = (
        "Searches the company's onboarding policy, IT setup checklist, "
        "benefits FAQ, and remote-work policy for grounded, relevant "
        "excerpts. Use this instead of guessing at company policy details."
    )
    args_schema: type[BaseModel] = RAGSearchInput

    def _run(self, query: str) -> str:
        results = rag_query(query, k=4)
        if not results:
            return "No relevant company documentation found."

        formatted = []
        for r in results:
            formatted.append(f"[Source: {r['source']}]\n{r['content']}")
        return "\n\n---\n\n".join(formatted)
