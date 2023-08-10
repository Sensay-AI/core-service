from pydantic import BaseModel


class GetVocabularyQuestions(BaseModel):
    category: str
    primary_language: str
    learning_language: str
    num_questions: int = 5
    num_answers: int = 4


class VocabularyAnswerCreate(BaseModel):
    answer_text: str
    is_correct: bool


class VocabularyQuestionCreate(BaseModel):
    question_text: str
    answers: list[VocabularyAnswerCreate]


class VocabularyPromptCreate(BaseModel):
    prompt: str
    category: str
    questions: list[VocabularyQuestionCreate]
    language: str
