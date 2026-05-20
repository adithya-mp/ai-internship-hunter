from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User
from schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, UserProfileUpdate, OAuthRequest
from utils.security import hash_password, verify_password, create_access_token, get_current_user
from services.ai_engine import generate_embedding

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pwd,
        full_name=user_data.full_name,
        profile_data={}
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/oauth", response_model=TokenResponse)
async def oauth_login(oauth_data: OAuthRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(User).where(User.email == oauth_data.email))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user for OAuth
        # Generate user embedding as empty for now, will get updated when profile is modified
        user = User(
            email=oauth_data.email,
            password_hash="",  # No password for OAuth
            full_name=oauth_data.full_name,
            profile_data={
                "photo_url": oauth_data.profile_photo or "",
                "provider": oauth_data.provider,
                "location": "India",
                "current_role": "Software Engineering Student",
                "target_role": "Software Engineer Intern",
                "linkedin_url": f"https://linkedin.com/in/{oauth_data.full_name.lower().replace(' ', '')}" if oauth_data.provider == "linkedin" else "",
                "portfolio_url": "",
                "experience": [],
                "education": [],
                "projects": []
            }
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # User exists, update profile photo/provider if not present
        profile = user.profile_data or {}
        updated = False
        if "photo_url" not in profile or not profile["photo_url"]:
            profile["photo_url"] = oauth_data.profile_photo or ""
            updated = True
        if "provider" not in profile:
            profile["provider"] = oauth_data.provider
            updated = True
        if updated:
            user.profile_data = profile
            db.add(user)
            await db.commit()
            await db.refresh(user)

    access_token = create_access_token(user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_profile(profile_data: UserProfileUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.profile_data is not None:
        current_user.profile_data = profile_data.profile_data

    # Re-generate embedding for user if profile changes
    from services.job_matcher import create_user_embedding
    if current_user.profile_data is not None:
        emb_data = {
            "bio": current_user.bio,
            **current_user.profile_data
        }
        current_user.embedding = await create_user_embedding(emb_data)
        
    await db.commit()
    await db.refresh(current_user)
    return current_user
