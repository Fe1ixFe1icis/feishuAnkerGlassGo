"""Evidence chain utilities."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Type of evidence source."""

    FACT = "fact"
    INFERENCE = "inference"


class Source(BaseModel):
    """A single evidence source."""

    type: SourceType = Field(..., description="Whether this is a fact or an inference")
    title: str = Field(..., description="Short title of the source")
    url: Optional[str] = Field(None, description="URL for fact sources")
    date: Optional[str] = Field(None, description="Publication date for fact sources")
    basis: Optional[str] = Field(
        None, description="Reasoning basis for inference sources"
    )
    confidence: float = Field(
        1.0, ge=0.0, le=1.0, description="Confidence level for inference sources"
    )

    def is_inference(self) -> bool:
        return self.type == SourceType.INFERENCE


class EvidenceClaim(BaseModel):
    """A claim attached to an evidence source."""

    claim: str = Field(..., description="The claim being made")
    source: Source = Field(..., description="Supporting evidence source")
    notes: Optional[str] = Field(None, description="Optional audit notes")


class EvidenceChain(BaseModel):
    """A chain of evidence claims."""

    claims: List[EvidenceClaim] = Field(default_factory=list)

    def add_fact(
        self,
        claim: str,
        title: str,
        url: Optional[str] = None,
        date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> "EvidenceChain":
        self.claims.append(
            EvidenceClaim(
                claim=claim,
                source=Source(
                    type=SourceType.FACT, title=title, url=url, date=date
                ),
                notes=notes,
            )
        )
        return self

    def add_inference(
        self,
        claim: str,
        basis: str,
        confidence: float = 0.7,
        notes: Optional[str] = None,
    ) -> "EvidenceChain":
        self.claims.append(
            EvidenceClaim(
                claim=claim,
                source=Source(
                    type=SourceType.INFERENCE,
                    title="AI inference",
                    basis=basis,
                    confidence=confidence,
                ),
                notes=notes,
            )
        )
        return self

    def facts(self) -> List[EvidenceClaim]:
        return [c for c in self.claims if c.source.type == SourceType.FACT]

    def inferences(self) -> List[EvidenceClaim]:
        return [c for c in self.claims if c.source.type == SourceType.INFERENCE]
