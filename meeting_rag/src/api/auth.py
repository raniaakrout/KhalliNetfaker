from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database.db import get_db
from database.crud import get_user_by_email, create_user
from schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Cookie config — httpOnly prevents JavaScript from reading the token (XSS protection)
COOKIE_NAME = "token"
COOKIE_MAX_AGE = 60 * 120  # 120 minutes (matches JWT_EXPIRATION_MINUTES)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with a hashed password."""
    # Check if user already exists
    existing_user = get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered.",
        )

    # Hash password
    hashed_pwd = hash_password(user_data.password)

    # Save user
    new_user = create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pwd,
    )

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Authenticate user, set httpOnly cookie and return JWT token in body."""
    # Find user by email
    user = get_user_by_email(db, email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    # Verify password
    if not verify_password(login_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    # Generate access token
    access_token = create_access_token(data={"user_id": str(user.user_id)})

    # ── Set httpOnly cookie ────────────────────────────────────────────────────
    # httpOnly=True → JavaScript cannot access this cookie (XSS protection).
    # samesite="lax" → cookie is sent on same-site requests + top-level navigations.
    # Also return the token in the body for backward compatibility with the
    # Axios Bearer interceptor (both mechanisms work in parallel).
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )

    return TokenResponse(
        access_token=access_token,
        user_id=str(user.user_id),
        username=str(user.username),
        email=str(user.email),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """Clear the httpOnly auth cookie."""
    response.delete_cookie(key=COOKIE_NAME, path="/")
