from fastapi import  FastAPI, Form, Depends
from fastapi.staticfiles import StaticFiles
import os
import sqlite3
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import Request, Response
from sqlalchemy.orm import Session

from database import Base
from database import SessionLocal
from database import engine

from models import create_workflow
from models import delete_workflow
from models import get_workflow
from models import get_workflows
from models import update_workflow
from models import run_workflow
from models import cancel_workflow_run
from models import create_workflow_run
from models import delete_workflow_run
from models import get_workflow_run_results

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    workflows = get_workflows(db)
    context = {
        "request": request,
        "workflows": workflows,
        "title": "Home",
    }
    response = templates.TemplateResponse("home.html", context)
    return response


@app.get("/edit/{item_id}", response_class=HTMLResponse)
def get_edit(request: Request, item_id: int, db: Session = Depends(get_db)):
    workflow = get_workflow(db, item_id)
    context = {"request": request, "workflow": workflow}
    return templates.TemplateResponse("workflow/form.html", context)


@app.put("/edit/{item_id}", response_class=HTMLResponse)
def put_edit(request: Request, item_id: int, content: str = Form(...), db: Session = Depends(get_db)):
    workflow = update_workflow(db, item_id, content)
    context = {"request": request, "workflow": workflow}
    return templates.TemplateResponse("workflow/item.html", context)


@app.delete("/delete/{item_id}", response_class=Response)
def delete(item_id: int, db: Session = Depends(get_db)):
    delete_workflow(db, item_id)


@app.delete("/delete_run/{item_id}", response_class=Response)
def delete(item_id: int, db: Session = Depends(get_db)):
    delete_workflow_run(db, item_id)

@app.post("/add_workflow", response_class=HTMLResponse)
def add_workflow(request: Request, content: str = Form(...), db: Session = Depends(get_db)):
    workflow = create_workflow(db, name=content)
    context = {"request": request, "workflow": workflow}
    return templates.TemplateResponse("workflow/item.html", context)

@app.post("/add_workflow_run/{item_id}", response_class=HTMLResponse)
def add_workflow_run(request: Request, item_id: int, content: str = Form(...), db: Session = Depends(get_db)):
    workflow_run = create_workflow_run(db, item_id, name=content)
    context = {"request": request, "workflow_run": workflow_run}
    return templates.TemplateResponse("workflow/run.html", context)

@app.post("/run/{item_id}", response_class=HTMLResponse)
def run(request: Request, item_id: int, db: Session = Depends(get_db)):
    workflow_run = run_workflow(db, item_id)
    context = {"request": request, "workflow_run": workflow_run}
    return templates.TemplateResponse("workflow/run.html", context)

@app.post("/cancel_run/{item_id}", response_class=HTMLResponse)
def cancel_run(request: Request, item_id: int, db: Session = Depends(get_db)):
    workflow_run = cancel_workflow_run(db, item_id)
    context = {"request": request, "workflow_run": workflow_run}
    return templates.TemplateResponse("workflow/item.html", context)

@app.get("/get_results/{item_id}", response_class=HTMLResponse)
def get_results(request: Request, item_id: int, db: Session = Depends(get_db)):
    workflow_run = get_workflow_run_results(db, item_id)
    context = {"request": request, "workflow_run": workflow_run}
    return templates.TemplateResponse("workflow/results.html", context)

@app.get("/get_results_image/{item_id}", response_class=FileResponse)
def get_results_image(request: Request, item_id: int, db: Session = Depends(get_db)):
    workflow_run = get_workflow_run_results(db, item_id)
    print(workflow_run.path)
    return workflow_run.path + "/results.png"
