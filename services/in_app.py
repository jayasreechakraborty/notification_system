from db.models import InAppMessage
from db.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
def save_in_app_message(user_id: str, message: str):
    try:
        with SessionLocal() as db:
            msg = InAppMessage(user_id=user_id, message=message)
            db.add(msg)
            db.commit()
            db.refresh(msg)
            return {"id": msg.id, "user_id": msg.user_id, "message": msg.message}
    except SQLAlchemyError:
        return None

def get_user_messages(user_id: str):
    try:
        with SessionLocal() as db:
            return [{"id": m.id, "message": m.message} for m in db.query(InAppMessage).filter_by(user_id=user_id)]
    except SQLAlchemyError:
        return []
