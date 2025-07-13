from sqlalchemy.orm import Session
from ..models.fulfillment import Fulfillment


def update_final_fulfillment_value(db: Session, id: int, new_fulfillment_value: int):
    fulfillment = db.query(Fulfillment).filter(Fulfillment.id == id).first()
    fulfillment.final_fulfillment_value = new_fulfillment_value
    db.commit()
    return fulfillment
