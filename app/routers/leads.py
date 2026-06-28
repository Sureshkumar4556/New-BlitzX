import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_db
from app.email_utils import send_lead_notification_email
from app.models import Lead
from app.rate_limit import limiter
from app.schemas import LeadCreate, LeadOut

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_lead(
    payload: LeadCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Honeypot: bots fill hidden fields. Pretend success without writing to DB.
    if payload.company:
        return LeadOut(
            id=uuid.UUID(int=0),
            name=payload.name,
            email=payload.email,
            service=payload.service,
            created_at=datetime.now(timezone.utc),
        )

    lead = Lead(
        name=payload.name.strip(),
        email=str(payload.email).lower(),
        phone=payload.phone,
        service=payload.service,
        message=payload.message.strip(),
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    background_tasks.add_task(send_lead_notification_email, lead.name, lead.email, lead.service, lead.message)

    return lead
