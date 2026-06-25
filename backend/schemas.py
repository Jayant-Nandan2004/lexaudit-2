"""Pydantic request/response schemas for the LexAudit API."""

from pydantic import BaseModel


class RuleSchema(BaseModel):
    """Payload for creating or updating a compliance rule."""

    title: str
    description: str
    category: str
    severity: str
