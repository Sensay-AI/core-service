from http import HTTPStatus
from typing import Any, Optional, Type

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.language import Language
from app.models.vocabulary import (
    Category,
    VocabularyAnswer,
    VocabularyPrompt,
    VocabularyQuestion,
)
from app.schemas.vocabulary import GetVocabularyHistoryQuestion, VocabularyPromptCreate


class CRUDVocabularyPrompt(CRUDBase[VocabularyPrompt, VocabularyPromptCreate, Any]):
    def create_with_category(
        self, db: Session, vocabularyPromptCreate: VocabularyPromptCreate, user_id: str
    ) -> Any:
        stmt = (
            insert(Category)
            .values(category_name=vocabularyPromptCreate.category, user_id=user_id)
            .on_conflict_do_update(
                index_elements=["category_name", "user_id"],
                set_={"category_name": vocabularyPromptCreate.category},
            )
            .returning(Category.id)
        )

        result = db.execute(stmt)
        insert_id = result.fetchone()[0]

        language: Optional[Language] = (
            db.query(Language)
            .filter(Language.language_name == vocabularyPromptCreate.language.upper())
            .first()
        )

        if not language:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"{vocabularyPromptCreate.language.upper()} does not support yet!",
            )

        vocabulary_prompt = VocabularyPrompt(
            prompt=vocabularyPromptCreate.prompt,
            category_id=insert_id,
            language_id=language.id,
        )

        questions = []
        answers = []
        for question in vocabularyPromptCreate.questions:
            vocabulary_question = VocabularyQuestion(
                question_text=question.question_text,
                prompt=vocabulary_prompt,
                language_id=language.id,
            )
            questions.append(vocabulary_question)
            for answer in question.answers:
                vocabulary_answer = VocabularyAnswer(
                    answer_text=answer.answer_text,
                    question=vocabulary_question,
                    is_correct=answer.is_correct,
                    language_id=language.id,
                )
                answers.append(vocabulary_answer)
        db.add(vocabulary_prompt)
        db.add_all(questions)
        db.add_all(answers)
        db.commit()

    def get_history_questions(
        self, db: Session, input: GetVocabularyHistoryQuestion, user_id: str
    ) -> list[Type[VocabularyPrompt]]:
        prompts = (
            db.query(VocabularyPrompt)
            .join(Category)
            .options(
                joinedload(VocabularyPrompt.questions).joinedload(
                    VocabularyQuestion.answers
                )
            )
            .filter(
                and_(
                    Category.id == input.category_id,
                    Category.user_id == user_id,
                    Language.language_name == input.learning_language.upper(),
                    VocabularyPrompt.is_valid,
                )
            )
            .limit(input.limit_prompts)
            .all()
        )

        return prompts
