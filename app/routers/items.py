import sys

sys.path.append("..")

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.auth import PermissionChecker
from app.permissions.models_permissions import Items
from app.database import get_db
from app.crud import items as crud
from app.schemas import ItemIn, Item, ItemUpdate

router = APIRouter(prefix="/v1")


@router.post("/items",
             dependencies=[Depends(PermissionChecker([Items.permissions.CREATE]))],
             response_model=Item, summary="Create a new item",
             tags=["Items"])
def create_item(item: ItemIn, db: Session = Depends(get_db)):
    """
    Creates a new item.
    """
    try:
        item_created = crud.create_item(db, item)
        return item_created
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.get("/items",
            dependencies=[Depends(PermissionChecker([Items.permissions.READ]))],
            response_model=List[Item], summary="Get all items",
            tags=["Items"])
def get_items(db: Session = Depends(get_db)):
    """
    Returns all items.
    """
    try:
        items = crud.get_items(db)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.delete("/items/{item_id}",
               dependencies=[Depends(PermissionChecker([Items.permissions.DELETE]))],
               summary="Delete an item", tags=["Items"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """
    Deletes an item.
    """
    try:
        crud.delete_item(db, item_id)
        return {"result": f"Item with ID {item_id} has been deleted successfully!"}
    except ValueError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")


@router.patch("/items/{item_id}",
              dependencies=[Depends(PermissionChecker([Items.permissions.READ, Items.permissions.UPDATE]))],
              response_model=Item,
              summary="Update an item", tags=["Items"])
def update_operating_spot(item_id: int, item_update: ItemUpdate,
                          db: Session = Depends(get_db)):
    """
    Updates an item.
    """
    try:
        item = crud.update_item(db, item_id, item_update)
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred. Report this message to support: {e}")
