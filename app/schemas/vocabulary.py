from pydantic import BaseModel


class GetVocabularyQuestions(BaseModel):
    category: str
    primary_language: str
    learning_language: str
    num_questions: int = 5
    num_answers: int = 4
