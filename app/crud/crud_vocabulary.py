from http import HTTPStatus
from typing import Any, List, Optional, Tuple, Type

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.language import Language
from app.models.vocabulary import (
    Category,
    VocabularyAnswer,
    VocabularyAnswerTranslation,
    VocabularyPrompt,
    VocabularyPromptTranslation,
    VocabularyQuestion,
    VocabularyQuestionTranslation,
)
from app.schemas.vocabulary import GetVocabularyHistoryQuestion, VocabularyPromptCreate


class CRUDVocabularyPrompt(CRUDBase[VocabularyPrompt, VocabularyPromptCreate, Any]):
    def _check_language(self, db: Session, language_name: str) -> int:
        language: Optional[Language] = (
            db.query(Language)
            .filter(Language.language_name == language_name.upper())
            .first()
        )

        if not language:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"{language_name.upper()} does not support yet!",
            )
        return language.id

    def _parse_question_answers(
        self,
        promptModel: VocabularyPrompt,
        promptCreate: VocabularyPromptCreate,
        learning_language_id: int,
        translated_language_id: int,
    ) -> Tuple[List[VocabularyQuestion], List[VocabularyAnswer]]:
        questions = []
        answers = []

        for question in promptCreate.questions:
            vocabulary_question = VocabularyQuestion(
                question_text=question.question_text,
                prompt=promptModel,
                language_id=learning_language_id,
            )
            vocabulary_translated_question = VocabularyQuestionTranslation(
                translated_text=question.translation,
                translated_language_id=translated_language_id,
                question=vocabulary_question,
            )
            questions.append(vocabulary_question)
            questions.append(vocabulary_translated_question)

            for answer in question.answers:
                vocabulary_answer = VocabularyAnswer(
                    answer_text=answer.answer_text,
                    question=vocabulary_question,
                    is_correct=answer.is_correct,
                    language_id=learning_language_id,
                )
                vocabulary_translated_answer = VocabularyAnswerTranslation(
                    translated_text=answer.translation,
                    translated_language_id=translated_language_id,
                    answer=vocabulary_answer,
                )
                answers.append(vocabulary_answer)
                answers.append(vocabulary_translated_answer)
        return questions, answers

    def create_with_category(
        self,
        db: Session,
        promptCreate: VocabularyPromptCreate,
        user_id: str,
    ) -> Any:
        stmt = (
            insert(Category)
            .values(category_name=promptCreate.category, user_id=user_id)
            .on_conflict_do_update(
                index_elements=["category_name", "user_id"],
                set_={"category_name": promptCreate.category},
            )
            .returning(Category.id)
        )

        result = db.execute(stmt)
        insert_id = result.fetchone()[0]

        learning_language_id = self._check_language(db, promptCreate.learning_language)
        translated_language_id = self._check_language(
            db, promptCreate.translated_language
        )

        prompt_obj = VocabularyPrompt(
            prompt=promptCreate.prompt,
            category_id=insert_id,
            language_id=learning_language_id,
        )

        translated_prompt_obj = VocabularyPromptTranslation(
            translated_language_id=translated_language_id,
            translated_text=promptCreate.translation,
            prompt=prompt_obj,
        )

        db.add(prompt_obj)
        db.add(translated_prompt_obj)

        questions, answers = self._parse_question_answers(
            prompt_obj, promptCreate, learning_language_id, translated_language_id
        )
        db.add_all(questions)
        db.add_all(answers)
        db.commit()

    def get_history_questions(
        self, db: Session, input: GetVocabularyHistoryQuestion, user_id: str
    ) -> list[Type[VocabularyPrompt]]:
        prompts = (
            db.query(VocabularyPrompt)
            .join(Category)
            .join(Language)
            .options(
                joinedload(VocabularyPrompt.language),
                joinedload(VocabularyPrompt.translations).joinedload(
                    VocabularyPromptTranslation.translated_language
                ),
                joinedload(VocabularyPrompt.questions).options(
                    joinedload(VocabularyQuestion.translations),
                    joinedload(VocabularyQuestion.answers).joinedload(
                        VocabularyAnswer.translations
                    ),
                ),
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
