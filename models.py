import os
import shutil
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship

from database import Base
import matplotlib.pyplot as plt


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    workflow_runs = relationship("WorkflowRun", back_populates="workflow")

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String)
    path = Column(String)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    workflow = relationship("Workflow", back_populates="workflow_runs")


def create_workflow(db: Session, name: str):
    workflow = Workflow(name=name, path=name)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    if not os.path.exists(name):
        os.mkdir(name)
    return workflow

def create_workflow_run(db: Session, item_id: int, name: str):
    workflow = get_workflow(db, item_id)
    workflow_run = WorkflowRun(name=name, status=None, workflow=workflow, path=os.path.join(workflow.path, name))
    db.add(workflow_run)
    db.commit()
    db.refresh(workflow)
    if not os.path.exists(workflow_run.path):
        os.mkdir(workflow_run.path)
    return workflow_run


def get_workflow(db: Session, item_id: int):
    return db.query(Workflow).filter(Workflow.id == item_id).first()

def get_workflow_run(db: Session, item_id: int):
    return db.query(WorkflowRun).filter(WorkflowRun.id == item_id).first()


def update_workflow(db: Session, item_id: int, name: str):
    workflow = get_workflow(db, item_id)
    if os.path.exists(workflow.path):
        os.rename(workflow.path, name)
    workflow.name = name
    workflow.path = name
    print(workflow.workflow_runs)
    for workflow_run in workflow.workflow_runs:
        print(workflow_run)
        workflow_run.path = os.path.join(workflow.path, workflow_run.name)
    db.commit()
    db.refresh(workflow)
    return workflow


def get_workflows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Workflow).offset(skip).limit(limit).all()


def delete_workflow(db: Session, item_id: int):
    workflow = get_workflow(db, item_id)
    if os.path.exists(workflow.path):
        shutil.rmtree(workflow.path)
    db.delete(workflow)
    db.commit()
    
def delete_workflow_run(db: Session, item_id: int):
    workflow_run = get_workflow_run(db, item_id)
    if os.path.exists(workflow_run.path):
        shutil.rmtree(workflow_run.path)
    db.delete(workflow_run)
    db.commit()

def run_workflow(db: Session, item_id: int):
    workflow_run = get_workflow_run(db, item_id)
    workflow_run.status = "running"
    db.commit()
    create_some_results(workflow_run.path, workflow_run.name)
    return workflow_run

def cancel_workflow_run(db: Session, item_id: int):
    workflow_run = get_workflow_run(db, item_id)
    workflow_run.status = "cancelled"
    db.commit()
    return workflow_run

def get_workflow_run_results(db: Session, item_id: int):
    workflow_run = get_workflow_run(db, item_id)
    return workflow_run

def create_some_results(path, name):
    x = [i for i in range(100)]
    y = [i**2 for i in x]
    plt.figure()
    plt.plot(x, y)
    plt.title(name)
    plt.savefig(path + "/results.png")
    plt.close()