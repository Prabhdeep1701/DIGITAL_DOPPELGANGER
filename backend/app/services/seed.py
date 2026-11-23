"""
Seed data — creates demo sessions on first startup so dashboards aren't empty.
"""

from sqlalchemy import select, func
from app.database.session import async_session
from app.models.models import Session
from app.simulation.profiles import (
    generate_human_like, generate_scripted_bot,
    generate_aggressive_bot, generate_slow_bot
)
from app.services.event_processor import create_session, process_batch


async def seed_demo_data():
    """Seed the database with demo sessions if empty."""
    async with async_session() as db:
        result = await db.execute(select(func.count(Session.id)))
        count = result.scalar()
        if count and count > 0:
            return  # Already seeded

        profiles = [
            ("human_like", generate_human_like, 60),
            ("scripted_bot", generate_scripted_bot, 50),
            ("aggressive_bot", generate_aggressive_bot, 40),
            ("slow_bot", generate_slow_bot, 50),
        ]

        for profile_name, generator, event_count in profiles:
            try:
                session = await create_session(db, is_simulated=profile_name)
                events = generator(event_count=event_count)
                await process_batch(db, str(session.id), events)
                await db.commit()
            except Exception as e:
                await db.rollback()
                print(f"Warning: Failed to seed {profile_name}: {e}")
