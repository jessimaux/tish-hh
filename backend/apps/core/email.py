import datetime
import hashlib
from random import randbytes

from fastapi import HTTPException, status, Request
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from sqlalchemy.orm import Session
from jinja2 import Environment, select_autoescape, PackageLoader
from jose import jwt

from apps.users.models import User
import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

env = Environment(
    loader=PackageLoader('main', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

async def send_verification_code(user: User, request: Request):
    template = env.get_template(f'verification.html')
    
    to_encode = {"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10), "username": user.username}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
    url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/auth/verifyemail/{encoded_jwt}"
    
    html = template.render(
        username = user.username,
        url = url
    )
        
    message = MessageSchema(
        subject="Verification code",
        recipients=[user.email],
        body=html,
        subtype=MessageType.html,
        )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='There was an error sending email')
        
async def send_retrieve_password_link(user: User, request: Request):
    template = env.get_template(f'password_retrieve.html')
    
    to_encode = {"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10), "username": user.username}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_RETRIEVE_PASSWORD_SECRET_KEY, settings.JWT_ALGORITHM)
    url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/auth/retrieve_password/{encoded_jwt}"
    
    html = template.render(
        username = user.username,
        url = url
    )
        
    message = MessageSchema(
        subject="Retrieve password link",
        recipients=[user.email],
        body=html,
        subtype=MessageType.html,
        )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='There was an error sending email')