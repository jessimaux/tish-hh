from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, foreign, remote
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(255), unique=True, nullable=True)
    password = Column(String(255))

    name = Column(String(255), nullable=True)
    bio = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(Boolean, nullable=True)
    country = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)

    image = relationship('Image',
                         back_populates='user',
                         uselist=False,
                         primaryjoin="and_(User.id == foreign(Image.object_id), Image.object_type == 'User')",
                         lazy='selectin')

    signs = relationship('Sign', back_populates='user', lazy='dynamic')
    links = relationship("Link", backref="user", lazy="selectin")

    following = relationship('User',
                             secondary="users__subscriptions",
                             primaryjoin="User.id==Subscription.subscriber_id",
                             secondaryjoin="User.id==Subscription.publisher_id",
                             lazy="dynamic")
    followers = relationship('User',
                             secondary="users__subscriptions",
                             primaryjoin="User.id==Subscription.publisher_id",
                             secondaryjoin="User.id==Subscription.subscriber_id",
                             lazy="dynamic")

    # TODO: under development
    # notifications = relationship('Notification',
    #                              secondary='notification_sender',
    #                              primaryjoin="User.id==NotificationSender.notifier_id",
    #                              secondaryjoin="NotificationSender.notification_id==Notification.id",
    #                              lazy='dynamic')

    is_verifed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Link(Base):
    __tablename__ = "users__links"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    link = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))


class Subscription(Base):
    __tablename__ = "users__subscriptions"

    subscriber_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    publisher_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
