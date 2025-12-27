from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db


class QuestionCreateRequest(BaseModel):
    user_id: int
    exam_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str  # A / B / C / D




router=APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/add-question")
def add_question(data: QuestionCreateRequest):
    db = get_db()
    cursor = db.cursor()

    # check admin
    cursor.execute("SELECT role FROM users WHERE id=%s", (data.user_id,))
    user = cursor.fetchone()

    if not user or user[0] != "admin":
        cursor.close()
        db.close()
        raise HTTPException(status_code=403, detail="Admin access required")

    # validate correct option
    if data.correct_option not in ("A", "B", "C", "D"):
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="Correct option must be A/B/C/D")

    # insert question
    cursor.execute(
        """
        INSERT INTO questions
        (exam_id, question, option_a, option_b, option_c, option_d, correct_option)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            data.exam_id,
            data.question,
            data.option_a,
            data.option_b,
            data.option_c,
            data.option_d,
            data.correct_option
        )
    )

    db.commit()
    cursor.close()
    db.close()

    return {"message": "Question added successfully"}
