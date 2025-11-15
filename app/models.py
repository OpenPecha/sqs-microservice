from pydantic import BaseModel

class Span(BaseModel):
    start: int
    end: int 

class Segments(BaseModel):
    segment_id: str
    span: Span

class SegmentsRelationRequest(BaseModel):
    manifestation_id: str
    segments: list[Segments]