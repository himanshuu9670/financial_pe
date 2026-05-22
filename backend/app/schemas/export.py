from uuid import UUID

from pydantic import BaseModel, Field


class ApplyEditsRequest(BaseModel):
    statement_id: UUID
    session_id: str | None = Field(
        default=None,
        description="Active or committed edit session. Uses committed metadata if omitted.",
    )
    validate_visual: bool = True


class VisualValidationSchema(BaseModel):
    text_match_ratio: float
    bbox_overlap_ratio: float
    regions_checked: int
    issues: list[str]
    passed: bool


class ApplyEditsResponse(BaseModel):
    statement_id: UUID
    status: str
    download_url: str
    original_preview_url: str
    edited_preview_url: str
    replacements_applied: int
    replacements_failed: int
    validation: VisualValidationSchema
    warnings: list[str] = Field(default_factory=list)
