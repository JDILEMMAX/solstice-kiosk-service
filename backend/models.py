from pydantic import BaseModel
from typing import Optional

class CheckInRequest(BaseModel):
    qr_code: str

class AttendeeResponse(BaseModel):
    id: int
    qr_code: str
    full_name: str
    email: Optional[str]
    ticket_type: str
    status: str
    checked_in_at: Optional[str]

class CheckInResponse(BaseModel):
    status: str
    message: str
    attendee: AttendeeResponse
    badge_printed: bool
    timestamp: str

class PrinterWebhookPayload(BaseModel):
    job_id: str
    qr_code: str
    status: str
    printed_at: str
