from fastapi import FastAPI
from database import init_db
from routes import notes
from routes.login import router as auth_router

app = FastAPI()
#Include Rotes
app.include_router(auth_router)
app.include_router(notes.router)
init_db()
