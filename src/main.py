from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes import recognition

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")
app.include_router(recognition.router)

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})