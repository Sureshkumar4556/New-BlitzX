"""
Seed the database with a sample user, order, and lead for local development.

Usage:
    python -m app.seed
"""
import asyncio

from app.database import AsyncSessionLocal, Base, engine
from app.models import Lead, Order, User
from app.security import hash_password


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        user = User(
            name="Demo User",
            email="demo@blitzxcreatives.com",
            password_hash=hash_password("password123"),
        )
        db.add(user)
        await db.flush()

        order = Order(
            user_id=user.id,
            service="Website Development",
            details="Need a modern portfolio + e-commerce site with cinematic UI.",
            budget="₹50,000 – ₹1,50,000",
            timeline="1 month",
            name=user.name,
            email=user.email,
            phone="9999999999",
            status="pending",
        )
        db.add(order)

        lead = Lead(
            name="Prospective Client",
            email="lead@example.com",
            phone="8888888888",
            service="SEO Optimization",
            message="Looking for SEO help for my e-commerce store.",
        )
        db.add(lead)

        await db.commit()
        print(f"Seeded user: {user.email} / password123")
        print(f"Seeded order: {order.id}")
        print(f"Seeded lead: {lead.id}")


if __name__ == "__main__":
    asyncio.run(seed())
