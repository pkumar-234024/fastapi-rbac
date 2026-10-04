from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import Item, Role, User
from schemas import ItemCreate, ItemOut, ItemUpdate
from security import get_current_user, require_roles

router = APIRouter(prefix="/items", tags=["Items"])


# CREATE  -> editor, admin
@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.editor, Role.admin)),
):
    item = Item(**data.model_dump(), owner_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# READ (list) -> any logged-in user
@router.get("/", response_model=list[ItemOut])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Item)
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


# READ (one) -> any logged-in user
@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return item


# UPDATE -> admin (any item) or editor (own items only)
@router.put("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.editor, Role.admin)),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    if user.role != Role.admin and item.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only edit your own items")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


# DELETE -> admin only
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.admin)),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    db.delete(item)
    db.commit()
