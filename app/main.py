from typing import List

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="TCC DevSecOps API",
    description="Microserviço simples usado como SUT no experimento DevSecOps.",
    version="1.0.0",
)


class ItemCreate(BaseModel):
    name: str
    description: str


class Item(ItemCreate):
    id: int


items = [
    {
        "id": 1,
        "name": "Item exemplo",
        "description": "Item usado no experimento",
    }
]


@app.get("/")
def read_root():
    return {"message": "TCC DevSecOps API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/items", response_model=List[Item])
def get_items():
    return items


@app.post("/items", response_model=Item)
def create_item(item: ItemCreate):
    new_item = {
        "id": len(items) + 1,
        "name": item.name,
        "description": item.description,
    }

    items.append(new_item)

    return new_item