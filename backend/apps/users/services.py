import datetime

from fastapi import HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import parse_obj_as
from jose import jwt, JWTError

import settings
from apps.uploader.services import UploaderService
from apps.auth.services import AuthService
from .repository import *
from .schemas import *


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repository = UserRepository(session)
        self.link_repository = LinkRepository(session)
        self.uploader_service = UploaderService(session)
        self.auth_service = AuthService(session)

    # TODO: rewrite email app, edit here
    async def create_user(self, user: UserCreate, request: Request, background_tasks: BackgroundTasks) -> UserRetrieve | None:
        if request.headers.get("Authorization"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Already authenticated")
        if await self.user_repository.check_email(user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email already registered")
        if await self.user_repository.check_username(user.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Username already registered")
        hashed_password = self.auth_service.get_hashed_password(user.password)
        user_obj = await self.user_repository.create(hashed_password, user.email, user.username)
        # background_tasks.add_task(send_verification_code, user_obj, request, session)
        return UserRetrieve.from_orm(user_obj)

    async def update_user(self, user_id: int, user: UserUpdate) -> UserRetrieve | None:
        if await self.user_repository.check_email_on_edit(user_id, user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email already in use")
        elif await self.user_repository.check_username_on_edit(user_id, user.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Username already in use")
        obj = await self.user_repository.update(user_id, user.dict())
        if not obj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="User doesnt exists")
        else:
            return UserRetrieve(obj)

    # TODO: what about general method to update foreign keys?
    async def update_links(self, user_id: int, links: list[LinkBase]) -> list[LinkBase] | None:
        if len(links) > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Max count of user's links is 5")
        else:
            db_links = await self.link_repository.get_by_user_id(user_id)
            actual_links = list()
            actual_links_id = list()

            for link in links:
                if getattr(link, 'id'):
                    link_obj = await self.link_repository.update(link.dict())
                else:
                    link_obj = await self.link_repository.create(user_id, link.dict())
                actual_links.append(link_obj)
                actual_links_id.append(link_obj.id)

            for link in db_links:
                if link.id not in actual_links_id:
                    await self.link_repository.delete(link.id)

            return parse_obj_as(list[LinkBase], actual_links)

    async def change_password(self, password_form: UserPasswordChange, user_id: int) -> int:
        user_obj = await self.user_repository.get_by_id(user_id)
        if self.auth_service.verify_password(password_form.old_password, user_obj.password):
            return await self.user_repository.update_password(user_id, password_form.new_password)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Incorrect old password")

    # TODO: rewrite email app, make changes here
    async def send_retrieve_password(self,
                                     password_retrieve_form: PasswordRetrieveBase,
                                     request: Request,
                                     background_tasks: BackgroundTasks) -> None:
        user_obj = await self.user_repository.get_by_username(password_retrieve_form.login) or await self.user_repository.get_by_email(password_retrieve_form.login)
        if not user_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User with this credentials doesnt exists")
        # background_tasks.add_task(send_retrieve_password_link, user_obj, request)

    async def check_retrieve_password_token(self, token: str) -> bool:
        try:
            jwt_decoded = jwt.decode(token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
            if datetime.datetime.fromtimestamp(jwt_decoded["exp"]) < datetime.datetime.now():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not validate token")
        user_obj = await self.user_repository.get_by_username(jwt_decoded["username"])
        if not user_obj:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid code or user doesn't exist")
        return True

    # TODO: rewrite id in jwt for retrieve
    async def retrieve_password(self, token: str) -> int:
        try:
            jwt_decoded = jwt.decode(token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
            if datetime.datetime.fromtimestamp(jwt_decoded["exp"]) < datetime.datetime.now():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not validate token")
        user_obj = await self.user_repository.get_by_username(jwt_decoded["username"])
        new_password = self.auth_service.get_hashed_password()
        result = await self.user_repository.update_password(user_obj.id, new_password)
        return result

    # TODO: rewrite id in jwt for retrieve
    async def verify_email(self, token: str) -> int:
        try:
            jwt_decoded = jwt.decode(token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
            if datetime.datetime.fromtimestamp(jwt_decoded["exp"]) < datetime.datetime.now():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not validate token")
        user_obj = await self.user_repository.get_by_username(jwt_decoded["username"])
        if not user_obj:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid code or user doesn't exist")
        if user_obj.is_verifed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Email can only be verified once")
        result = await self.user_repository.verify(user_obj.id)
        return result

    async def upload_photo(self, image_id: int, user_id: int) -> ImageBase | None:
        image_obj = await self.uploader_service.image_repository.link_to_user(image_id, user_id)
        return ImageBase(image_obj)

    async def delete_photo(self, image_id: int, user_id: int) -> int:
        return await self.uploader_service.delete(image_id, user_id)


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.profile_repository = ProfileRepository(session)
        
    async def get_profile(self, username: str) -> Profile | None:
        user_obj = await self.user_repository.get_by_username(username)
        if not user_obj:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User doesn't exist")
        profile_obj = await self.profile_repository.get_profile(user_obj.id)
        return Profile(profile_obj)

    async def get_followers(self, username: str) -> list[UserRetrieve] | None:
        return await self.user_repository.get_followers(username)

    async def get_following(self, username: str) -> list[UserRetrieve] | None:
        return await self.user_repository.get_following(username)


class SubscriptionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.subscription_repository = SubscriptionRepository(session)

    async def check_follow(self, username: str, current_user_id: int) -> bool:
        subscription_obj = await self.subscription_repository.get(current_user_id, username)
        if subscription_obj:
            return True
        else:
            return False
        
    async def follow(self, username: str, current_user_id: int) -> bool:
        if await self.check_follow(username, current_user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Already followed')
        else:
            subscribe_obj = await self.subscription_repository.create(current_user_id, username)
        if subscribe_obj:
            return True
        else:
            return False
    
    async def unfollow(self, username: str, current_user_id: int) -> bool:
        if not await self.check_follow(username, current_user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Doesnt followed')
        deleted_row = await self.subscription_repository.delete(current_user_id, username)
        if deleted_row != 0:
            return True
        else:
            return False
    