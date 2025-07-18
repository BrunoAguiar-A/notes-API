from fastapi import FastAPI
from database import init_db
from routes import notes


app = FastAPI()
init_db()

#Include Rotes
app.include_router(notes.router)
