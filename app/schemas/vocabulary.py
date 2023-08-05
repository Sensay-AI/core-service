from typing import List, Optional
from pydantic import BaseModel


class GetVocabularyQuestions(BaseModel):
    category: str
    primary_language: str
    learning_language: str
    num_questions: Optional[int] = 5
    num_answers: Optional[int] = 4
