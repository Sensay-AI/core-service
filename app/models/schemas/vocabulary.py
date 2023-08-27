from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field

DIFFICULT_LEVELS = {1: "EASY", 2: "INTERMEDIATE", 3: "ADVANCED"}


class GetVocabularyQuestions(BaseModel):
    category: str
    level: Optional[int] = Field(
        None, description="DEPRECATED: Use `level_type` instead of this"
    )
    level_type: str = Field(
        DIFFICULT_LEVELS[1],
        description="Difficult level of the lesson, value: <'EASY','INTERMEDIATE','ADVANCED'>",
    )
    translated_language: str
    learning_language: str
    num_questions: int = 5
    num_answers: int = 3


class GetVocabularyHistoryQuestion(BaseModel):
    category_id: int
    learning_language: str


class VocabularyAnswerCreate(BaseModel):
    answer_text: str
    is_correct: bool
    translation: str


class VocabularyQuestionCreate(BaseModel):
    question_text: str
    answers: list[VocabularyAnswerCreate]
    translation: str


class VocabularyPromptCreate(BaseModel):
    prompt: str
    category: str
    questions: list[VocabularyQuestionCreate]
    learning_language: str
    translated_language: str
    translation: str
    difficulty_level: str
