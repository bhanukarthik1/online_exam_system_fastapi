from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db



from pydantic import BaseModel
from typing import List

class Answer(BaseModel):
    question_id: int
    selected_option: str

class SubmitExamRequest(BaseModel):
    student_id: int
    exam_id: int
    answers: List[Answer]


router=APIRouter(prefix="/student", tags=["student"])

@router.get("/exams")
def view_exams():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, title, duration, total_marks FROM exams")
    exams = cursor.fetchall()

    cursor.close()
    db.close()

    return exams


@router.get("/exam/{exam_id}/questions")
def view_questions(exam_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, question, option_a, option_b, option_c, option_d
        FROM questions
        WHERE exam_id = %s
        """,
        (exam_id,)
    )

    questions = cursor.fetchall()

    cursor.close()
    db.close()

    return questions



@router.post("/submit")
def submit_exam(data: SubmitExamRequest):
    db = get_db()
    cursor = db.cursor()

    # check duplicate submission
    cursor.execute(
        "SELECT id FROM results WHERE student_id=%s AND exam_id=%s",
        (data.student_id, data.exam_id)
    )
    if cursor.fetchone():
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="Exam already submitted")

    for ans in data.answers:
        cursor.execute(
            """
            INSERT INTO student_answers
            (student_id, exam_id, question_id, selected_option)
            VALUES (%s,%s,%s,%s)
            """,
            (data.student_id, data.exam_id, ans.question_id, ans.selected_option)
        )

    db.commit()
    cursor.close()
    db.close()

    return {"message": "Answers submitted successfully"}



@router.post("/evaluate")
def evaluate_exam(student_id: int, exam_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # prevent re-evaluation
    cursor.execute(
        "SELECT id FROM results WHERE student_id=%s AND exam_id=%s",
        (student_id, exam_id)
    )
    if cursor.fetchone():
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="Result already exists")

    # calculate score
    cursor.execute(
        """
        SELECT sa.selected_option, q.correct_option
        FROM student_answers sa
        JOIN questions q ON sa.question_id = q.id
        WHERE sa.student_id=%s AND sa.exam_id=%s
        """,
        (student_id, exam_id)
    )

    answers = cursor.fetchall()
    score = 0

    for ans in answers:
        if ans["selected_option"] == ans["correct_option"]:
            score += 1

    # store result
    cursor.execute(
        "INSERT INTO results (student_id, exam_id, score) VALUES (%s,%s,%s)",
        (student_id, exam_id, score)
    )

    db.commit()
    cursor.close()
    db.close()

    return {
        "message": "Exam evaluated successfully",
        "score": score
    }




@router.get("/result")
def view_result(student_id: int, exam_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT e.title, r.score, r.submitted_at
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.student_id=%s AND r.exam_id=%s
        """,
        (student_id, exam_id)
    )

    result = cursor.fetchone()

    cursor.close()
    db.close()

    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    return result



