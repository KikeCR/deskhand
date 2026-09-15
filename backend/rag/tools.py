"""CrewAI tool that lets the Research Agent query the company-docs vectorstore."""

from __future__ import annotations

import re

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from rag.retriever import query as rag_query

# ingest.chunk_markdown keeps each chunk's "## Header" line as a prefix so
# the chunk is self-describing once retrieved out of context. That raw "##"
# syntax is only useful as a section label for whoever reads this tool's
# output; agents tend to quote it verbatim into their findings, which then
# shows up as stray "##" characters in front of a user reading the final
# checklist. Strip the markdown header markers here, at the tool boundary,
# so the label survives but the raw syntax doesn't leak downstream.
_HEADER_MARKER = re.compile(r"(?m)^#+\s*")


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
            content = _HEADER_MARKER.sub("", r["content"])
            formatted.append(f"[Source: {r['source']}]\n{content}")
        return "\n\n---\n\n".join(formatted)
