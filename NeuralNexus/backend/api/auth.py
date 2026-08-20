"""
backend/api/auth.py
-------------------
Authentication and login endpoints.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.auth_utils import (
    create_access_token,
    hash_password,
    verify_password,
)
from database.connection import get_db
from database.models import Student
from database.repository import (
    create_admin,
    get_admin_by_email,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ============================================================
# REQUEST / RESPONSE SCHEMAS
# ============================================================

class AdminRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    roll_number: str | None = None
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str
    email: str


# ============================================================
# ADMIN REGISTER
# ============================================================

@router.post(
    "/admin/register",
    response_model=TokenResponse,
    status_code=201,
)
def register_admin(
    payload: AdminRegisterRequest,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    existing = get_admin_by_email(db, email)

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Admin with this email already exists.",
        )

    password_hash = hash_password(payload.password)

    admin = create_admin(
        db,
        name=payload.name.strip(),
        email=email,
        password_hash=password_hash,
    )

    token = create_access_token(
        {
            "sub": str(admin.id),
            "role": "admin",
            "email": admin.email,
        }
    )

    return TokenResponse(
        access_token=token,
        role="admin",
        user_id=admin.id,
        name=admin.name,
        email=admin.email,
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@router.post(
    "/admin/login",
    response_model=TokenResponse,
)
def admin_login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    if not payload.email:
        raise HTTPException(
            status_code=422,
            detail="Admin email is required.",
        )

    email = str(payload.email).strip().lower()

    admin = get_admin_by_email(db, email)

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Admin account not found.",
        )

    if not admin.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Admin account has no password.",
        )

    if not verify_password(
        payload.password,
        admin.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect admin password.",
        )

    token = create_access_token(
        {
            "sub": str(admin.id),
            "role": "admin",
            "email": admin.email,
        }
    )

    return TokenResponse(
        access_token=token,
        role="admin",
        user_id=admin.id,
        name=admin.name,
        email=admin.email,
    )


# ============================================================
# STUDENT LOOKUP
# ============================================================

def find_student_for_login(
    db: Session,
    email: str | None,
    roll_number: str | None,
) -> Student | None:
    """
    Find student using email, roll number or student code.

    Email matching is case-insensitive and whitespace-safe.
    Roll number / student code matching is also whitespace-safe.
    """

    # --------------------------------------------------------
    # 1. Email lookup
    # --------------------------------------------------------
    if email:
        clean_email = email.strip().lower()

        student = db.execute(
            select(Student).where(
                func.lower(func.trim(Student.email)) == clean_email
            )
        ).scalar_one_or_none()

        if student:
            return student

    # --------------------------------------------------------
    # 2. Roll number lookup
    # --------------------------------------------------------
    if roll_number:
        clean_roll = roll_number.strip()

        student = db.execute(
            select(Student).where(
                func.trim(Student.roll_number) == clean_roll
            )
        ).scalar_one_or_none()

        if student:
            return student

        # ----------------------------------------------------
        # 3. Student code lookup
        # ----------------------------------------------------
        student = db.execute(
            select(Student).where(
                func.trim(Student.student_code) == clean_roll
            )
        ).scalar_one_or_none()

        if student:
            return student

    return None


# ============================================================
# STUDENT LOGIN
# ============================================================

@router.post(
    "/student/login",
    response_model=TokenResponse,
)
def student_login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    email = (
        str(payload.email).strip().lower()
        if payload.email
        else None
    )

    roll_number = (
        payload.roll_number.strip()
        if payload.roll_number
        else None
    )

    if not email and not roll_number:
        raise HTTPException(
            status_code=422,
            detail="Provide student email or roll number.",
        )

    # --------------------------------------------------------
    # Find student
    # --------------------------------------------------------
    student = find_student_for_login(
        db,
        email=email,
        roll_number=roll_number,
    )

    if not student:
        raise HTTPException(
            status_code=401,
            detail="Student account not found. Please register first.",
        )

    # --------------------------------------------------------
    # Password check
    # --------------------------------------------------------
    if not student.password_hash:
        raise HTTPException(
            status_code=401,
            detail="This student account has no password.",
        )

    if not verify_password(
        payload.password,
        student.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect student email/roll number or password.",
        )

    # --------------------------------------------------------
    # Update last login
    # --------------------------------------------------------
    student.last_login_at = datetime.utcnow()

    db.add(student)
    db.commit()
    db.refresh(student)

    # --------------------------------------------------------
    # Create JWT
    # --------------------------------------------------------
    token = create_access_token(
        {
            "sub": str(student.id),
            "role": "student",
            "email": student.email,
        }
    )

    return TokenResponse(
        access_token=token,
        role="student",
        user_id=student.id,
        name=student.full_name,
        email=student.email,
    )
