from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from database import Base

    
class Notification(Base):
    __tablename__ = 'notification'
    
    id = Column(Integer, primary_key=True, index=True)
    notification_type_id = Column(Integer, ForeignKey("notification_type.id", ondelete='CASCADE'))
    object_type = Column(String(255))
    object_id = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

class NotificationType(Base):
    __tablename__ = 'notification_type'
    
    id = Column(Integer, primary_key=True, index=True)
    template = Column(String)
    description = Column(String(255))
    

class NotificationSender(Base):
    __tablename__ = 'notification_sender'
    
    id = Column(Integer, primary_key=True, index=True)
    triger_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    notifier_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    notification_id = Column(Integer, ForeignKey('notification.id'))