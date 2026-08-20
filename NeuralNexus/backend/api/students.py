"""
backend/api/students.py
Student registration, profile and identity document APIs.
"""

from __future__ import annotations

import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.auth_utils import (
    get_current_user,
    hash_password,
    require_admin,
    require_student,
)
from database.connection import get_db
from database.repository import (
    create_student,
    get_student_by_code,
    get_student_by_email,
    get_student_by_id,
    get_student_by_roll,
    list_published_reports_for_student,
    list_students,
    update_student_identity,
)
from detection.face_detection import (
    compare_id_card_and_passport,
    get_primary_face_embedding,
)


router = APIRouter(
    prefix="/api/students",
    tags=["students"],
)


PROFILE_IMAGE_DIR = os.path.join(
    "data",
    "student_profiles",
)

ID_CARD_DIR = os.path.join(
    "data",
    "id_cards",
)

PASSPORT_DIR = os.path.join(
    "data",
    "passport_photos",
)


# ============================================================
# RESPONSE MODELS
# ============================================================

class StudentOut(BaseModel):

    id: int
    student_code: str
    roll_number: str | None

    full_name: str
    email: str
    course: str | None

    identity_verified: bool

    ocr_match_score: float | None
    face_match_score_reg: float | None
    face_match_score: float | None
    face_match_status: str | None

    id_card_image_path: str | None
    passport_image_path: str | None

    created_at: str
    last_login_at: str | None

    model_config = ConfigDict(from_attributes=True)


class StudentList(BaseModel):

    students: list[StudentOut]
    total: int


class IdentityVerifyOut(BaseModel):

    student_id: int
    identity_verified: bool

    ocr_match_score: float | None
    face_match_score: float | None
    face_match_status: str | None

    message: str


class NoticeOut(BaseModel):

    report_id: int
    student_id: int
    student_name: str | None = None
    student_roll: str | None = None
    risk_score: float
    risk_level: str
    summary: str

    pdf_path: str | None
    created_at: str


# ============================================================
# HELPER
# ============================================================

def _save_upload(
    upload: UploadFile,
    directory: str,
    prefix: str,
) -> str:

    os.makedirs(
        directory,
        exist_ok=True,
    )

    original_name = upload.filename or ""

    extension = os.path.splitext(
        original_name
    )[1].lower()

    if extension not in [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]:
        extension = ".jpg"

    filename = (
        f"{prefix}_"
        f"{uuid.uuid4().hex[:10]}"
        f"{extension}"
    )

    path = os.path.join(
        directory,
        filename,
    )

    with open(path, "wb") as file:

        file.write(
            upload.file.read()
        )

    return path


def _file_url(
    path: str | None,
    url_prefix: str,
) -> str | None:

    if not path:
        return None

    clean = path.replace("\\", "/")

    filename = os.path.basename(
        clean
    )

    return f"{url_prefix}/{filename}"


def _student_to_response(
    student,
) -> StudentOut:
    ocr_score = student.ocr_match_score
    if ocr_score is None and student.id_card_image_path and os.path.exists(student.id_card_image_path):
        try:
            from detection.ocr_detection import compute_id_card_ocr_match
            calc_ocr, _ = compute_id_card_ocr_match(
                student.id_card_image_path,
                student.full_name,
                student.roll_number or student.student_code,
            )
            ocr_score = calc_ocr
            student.ocr_match_score = ocr_score
        except Exception:
            pass

    face_score = (
        student.face_match_score
        if student.face_match_score is not None
        else student.face_match_score_reg
    )
    if face_score is None and student.id_card_image_path and (student.passport_image_path or student.profile_image_path):
        passport_p = student.passport_image_path or student.profile_image_path
        if os.path.exists(student.id_card_image_path) and os.path.exists(passport_p):
            try:
                from detection.face_detection import compare_id_card_and_passport
                f_score, f_status = compare_id_card_and_passport(
                    student.id_card_image_path,
                    passport_p,
                )
                face_score = f_score
                student.face_match_score = f_score
                student.face_match_score_reg = f_score
                student.face_match_status = f_status
            except Exception:
                pass

    is_verified = bool(
        student.identity_verified or
        ((ocr_score and ocr_score >= 60.0) and (face_score and face_score >= 50.0))
    )
    student.identity_verified = is_verified

    return StudentOut(
        id=student.id,

        student_code=student.student_code,

        roll_number=student.roll_number,

        full_name=student.full_name,

        email=student.email,

        course=student.course,

        identity_verified=is_verified,

        ocr_match_score=ocr_score,

        face_match_score_reg=face_score,

        face_match_score=face_score,

        face_match_status=(
            student.face_match_status or ("Matched" if face_score and face_score >= 50 else None)
        ),

        id_card_image_path=_file_url(
            student.id_card_image_path,
            "/uploads/id-cards",
        ),

        passport_image_path=_file_url(
            student.passport_image_path
            or student.profile_image_path,
            "/uploads/passport-photos",
        ),

        created_at=(
            student.created_at.isoformat()
            if student.created_at
            else ""
        ),

        last_login_at=(
            student.last_login_at.isoformat()
            if student.last_login_at
            else None
        ),
    )


# ============================================================
# STUDENT REGISTRATION
# ============================================================

@router.post(
    "",
    response_model=StudentOut,
    status_code=201,
)
@router.post(
    "/register",
    response_model=StudentOut,
    status_code=201,
)
def register_student(

    student_code: str = Form(...),

    full_name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    course: str | None = Form(None),

    profile_image: UploadFile | None = File(None),

    passport: UploadFile | None = File(None),

    id_card: UploadFile | None = File(None),

    db: Session = Depends(get_db),
):

    student_code = student_code.strip()

    email = email.strip().lower()

    full_name = full_name.strip()

    if get_student_by_code(
        db,
        student_code,
    ):

        raise HTTPException(
            status_code=409,
            detail="Student ID / roll number already registered.",
        )

    if get_student_by_email(
        db,
        email,
    ):

        raise HTTPException(
            status_code=409,
            detail="Email already registered.",
        )

    if not password:
        raise HTTPException(
            status_code=422,
            detail="Password is required.",
        )

    # --------------------------------------------------------
    # Passport photo
    # --------------------------------------------------------

    passport_file = (
        passport
        or profile_image
    )

    passport_path = None

    if (
        passport_file
        and passport_file.filename
    ):

        passport_path = _save_upload(
            passport_file,
            PASSPORT_DIR,
            f"passport_{student_code}",
        )

    # --------------------------------------------------------
    # ID card
    # --------------------------------------------------------

    id_card_path = None

    if (
        id_card
        and id_card.filename
    ):

        id_card_path = _save_upload(
            id_card,
            ID_CARD_DIR,
            f"idcard_{student_code}",
        )

    # --------------------------------------------------------
    # Face embedding
    # --------------------------------------------------------

    embedding = None

    if passport_path:

        try:

            embedding = get_primary_face_embedding(
                passport_path
            )

        except Exception:

            embedding = None

    # --------------------------------------------------------
    # Identity verification
    # --------------------------------------------------------

    face_score = None
    face_status = None

    if (
        id_card_path
        and passport_path
    ):

        try:

            face_score, face_status = (
                compare_id_card_and_passport(
                    id_card_path,
                    passport_path,
                )
            )

        except Exception:

            face_score = None
            face_status = "Not available"

    # --------------------------------------------------------
    # Real-Time OCR Text Match
    # --------------------------------------------------------
    ocr_score = None
    if id_card_path and os.path.exists(id_card_path):
        try:
            from detection.ocr_detection import compute_id_card_ocr_match
            ocr_score, _ = compute_id_card_ocr_match(
                id_card_path,
                full_name,
                student_code,
            )
        except Exception:
            ocr_score = None

    identity_verified = bool(
        (ocr_score and ocr_score >= 60.0) and
        (face_score and face_score >= 50.0)
    )

    password_hash = hash_password(
        password
    )

    student = create_student(

        db,

        student_code=student_code,

        roll_number=student_code,

        full_name=full_name,

        email=email,

        course=course,

        password_hash=password_hash,

        profile_image_path=passport_path,

        id_card_image_path=id_card_path,

        passport_image_path=passport_path,

        face_embedding=embedding,

        identity_verified=identity_verified,

        ocr_match_score=ocr_score,

        face_match_score_reg=face_score,

        face_match_score=face_score,

        face_match_status=face_status,
    )

    return _student_to_response(
        student
    )


# ============================================================
# STUDENT PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=StudentOut,
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_student
    ),
):
    student_id = int(
        current_user["sub"]
    )

    student = get_student_by_id(
        db,
        student_id,
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    res = _student_to_response(
        student
    )

    try:
        db.add(student)
        db.commit()
    except Exception:
        pass

    return res


# ============================================================
# UPDATE STUDENT DOCUMENTS
# ============================================================

@router.post(
    "/me/identity-documents",
    response_model=StudentOut,
)
@router.put(
    "/me/identity-documents",
    response_model=StudentOut,
)
def update_my_identity_documents(

    passport: UploadFile | None = File(None),

    profile_image: UploadFile | None = File(None),

    id_card: UploadFile | None = File(None),

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        require_student
    ),
):

    student_id = int(
        current_user["sub"]
    )

    student = get_student_by_id(
        db,
        student_id,
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    passport_file = (
        passport
        or profile_image
    )

    if (
        passport_file
        and passport_file.filename
    ):

        passport_path = _save_upload(
            passport_file,
            PASSPORT_DIR,
            f"passport_{student.student_code}",
        )

        student.passport_image_path = (
            passport_path
        )

        student.profile_image_path = (
            passport_path
        )

        try:

            student.face_embedding = (
                get_primary_face_embedding(
                    passport_path
                )
            )

        except Exception:

            pass

    if (
        id_card
        and id_card.filename
    ):

        id_card_path = _save_upload(
            id_card,
            ID_CARD_DIR,
            f"idcard_{student.student_code}",
        )

        student.id_card_image_path = (
            id_card_path
        )

    # --------------------------------------------------------
    # Face matching
    # --------------------------------------------------------

    if (
        student.id_card_image_path
        and (
            student.passport_image_path
            or student.profile_image_path
        )
    ):

        try:

            score, status_text = (
                compare_id_card_and_passport(
                    student.id_card_image_path,
                    student.passport_image_path
                    or student.profile_image_path,
                )
            )

        except Exception:
            pass

    # --------------------------------------------------------
    # OCR ID Card matching
    # --------------------------------------------------------
    if student.id_card_image_path and os.path.exists(student.id_card_image_path):
        try:
            from detection.ocr_detection import compute_id_card_ocr_match
            ocr_score, _ = compute_id_card_ocr_match(
                student.id_card_image_path,
                student.full_name,
                student.roll_number or student.student_code,
            )
            student.ocr_match_score = ocr_score
        except Exception:
            pass

    # Update verification status
    is_verified = bool(
        (student.ocr_match_score and student.ocr_match_score >= 60.0) and
        (student.face_match_score and student.face_match_score >= 50.0)
    )
    student.identity_verified = is_verified

    db.add(student)

    db.commit()

    db.refresh(student)

    return _student_to_response(
        student
    )


# ============================================================
# ADMIN VERIFY IDENTITY
# ============================================================

@router.post(
    "/{student_id}/verify",
    response_model=IdentityVerifyOut,
)
def verify_identity(

    student_id: int,

    db: Session = Depends(get_db),

    _admin: dict = Depends(
        require_admin
    ),
):

    student = get_student_by_id(
        db,
        student_id,
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    face_score = None
    face_status = "Not available"

    if (
        student.id_card_image_path
        and (
            student.passport_image_path
            or student.profile_image_path
        )
    ):

        try:

            face_score, face_status = (
                compare_id_card_and_passport(
                    student.id_card_image_path,
                    student.passport_image_path
                    or student.profile_image_path,
                )
            )

        except Exception:

            pass

    # No fake OCR value.
    ocr_score = student.ocr_match_score

    # Identity is verified only when real verification
    # information is available and passes.
    verified = False

    if (
        ocr_score is not None
        and ocr_score >= 0.7
    ):

        verified = (
            face_score is None
            or face_score >= 50.0
        )

    updated = update_student_identity(

        db,

        student_id,

        identity_verified=verified,

        ocr_match_score=ocr_score,

        face_match_score_reg=face_score,

        face_match_score=face_score,

        face_match_status=face_status,
    )

    return IdentityVerifyOut(

        student_id=student_id,

        identity_verified=verified,

        ocr_match_score=ocr_score,

        face_match_score=face_score,

        face_match_status=face_status,

        message=(
            "Identity verified successfully."
            if verified
            else "Identity verification is incomplete or failed."
        ),
    )


# ============================================================
# STUDENT NOTICES
# ============================================================

@router.get(
    "/me/notices",
    response_model=list[NoticeOut],
)
def get_my_notices(

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        require_student
    ),
):

    student_id = int(
        current_user["sub"]
    )

    reports = (
        list_published_reports_for_student(
            db,
            student_id,
        )
    )

    out = []
    for report in reports:
        if report.student_id != student_id:
            continue
        out.append(
            NoticeOut(
                report_id=report.id,
                student_id=report.student_id,
                student_name=report.student.full_name if report.student else None,
                student_roll=(report.student.roll_number or report.student.student_code) if report.student else None,
                risk_score=report.risk_score,
                risk_level=report.risk_level,
                summary=report.summary,
                pdf_path=report.pdf_path,
                created_at=(
                    report.created_at.isoformat()
                    if report.created_at
                    else ""
                ),
            )
        )
    return out


@router.get(
    "/{student_id}/notices",
    response_model=list[NoticeOut],
)
def get_student_notices_admin(

    student_id: int,

    db: Session = Depends(get_db),

    _admin: dict = Depends(
        require_admin
    ),
):

    reports = (
        list_published_reports_for_student(
            db,
            student_id,
        )
    )

    return [
        NoticeOut(
            report_id=report.id,
            student_id=report.student_id,
            student_name=report.student.full_name if report.student else None,
            student_roll=(report.student.roll_number or report.student.student_code) if report.student else None,
            risk_score=report.risk_score,
            risk_level=report.risk_level,
            summary=report.summary,
            pdf_path=report.pdf_path,
            created_at=(
                report.created_at.isoformat()
                if report.created_at
                else ""
            ),
        )
        for report in reports
        if report.student_id == student_id
    ]


# ============================================================
# ADMIN: LIST STUDENTS
# ============================================================

@router.get(
    "",
    response_model=StudentList,
)
def list_all_students(

    limit: int = 100,

    offset: int = 0,

    db: Session = Depends(get_db),

    _admin: dict = Depends(
        require_admin
    ),
):

    students = list_students(
        db,
        limit=limit,
        offset=offset,
    )

    return StudentList(
        students=[
            _student_to_response(student)
            for student in students
        ],
        total=len(students),
    )


# ============================================================
# ADMIN: STUDENT BY ID
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentOut,
)
def get_student(

    student_id: int,

    db: Session = Depends(get_db),

    _admin: dict = Depends(
        require_admin
    ),
):

    student = get_student_by_id(
        db,
        student_id,
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return _student_to_response(
        student
    )


# ============================================================
# ADMIN: STUDENT BY CODE
# ============================================================

@router.get(
    "/by-code/{student_code}",
    response_model=StudentOut,
)
def get_student_by_code_route(

    student_code: str,

    db: Session = Depends(get_db),

    _admin: dict = Depends(
        require_admin
    ),
):

    student = get_student_by_code(
        db,
        student_code,
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return _student_to_response(
        student
    )
