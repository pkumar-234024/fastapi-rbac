from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, SessionLocal, engine
from models import Role, User
from routers import auth, items, users
from security import hash_password


def seed_admin():
    """Create a default admin on first run. CHANGE THIS PASSWORD."""
    with SessionLocal() as db:
        if not db.query(User).filter(User.role == Role.admin).first():
            db.add(
                User(
                    username="admin",
                    hashed_password=hash_password("admin123"),
                    role=Role.admin,
                )
            )
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_admin()
    yield


app = FastAPI(title="Items API with Role-Based Auth", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs"}
