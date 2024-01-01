from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Item
from app.schemas import ItemIn, ItemUpdate


def create_item(db: Session, item: ItemIn):
    item = Item(
        name=item.name
    )
    db.add(item)
    db.commit()
    return item


def get_items(db: Session):
    items = list(db.scalars(
        select(Item)
    ))
    return items


def delete_item(db: Session, item_id: int):
    item = db.scalar(
        select(Item)
        .where(Item.id == item_id)
    )
    if not item:
        raise ValueError(
            f"There is no item with ID {item_id}")
    else:
        item.delete()
        db.commit()


def update_item(db: Session, item_id: int, item_update: ItemUpdate):
    item = db.scalar(
        select(Item)
        .where(Item.id == item_id)
    )
    if not item:
        raise ValueError(
            f"There isn't any item with ID {item_id}")

    updated_item = item_update.model_dump(exclude_unset=True)
    for key, value in updated_item.items():
        setattr(item, key, value)
    db.commit()
    return item
