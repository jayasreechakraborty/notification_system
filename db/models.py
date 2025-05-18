from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class InAppMessage(Base):
    __tablename__ = "in_app_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<InAppMessage(id={self.id}, user_id={self.user_id})>"