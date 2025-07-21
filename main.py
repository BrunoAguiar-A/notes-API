from fastapi import FastAPI
from database import init_db
from routes import notes, user, auth, share
from routes.login import router as auth_router


app = FastAPI()
#Include Rotes
app.include_router(auth_router)
app.include_router(notes.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(share.router)
init_db()
