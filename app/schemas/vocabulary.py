from pydantic import BaseModel


class GetVocabularyQuestions(BaseModel):
    category: str
    translated_language: str
    learning_language: str
    num_questions: int = 5
    num_answers: int = 4


class GetVocabularyHistoryQuestion(BaseModel):
    category_id: int
    limit_prompts: int = 10
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
