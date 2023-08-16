from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, List, Optional, Type

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

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
from app.repositories.base_repository import BaseRepository
from app.schemas.vocabulary import GetVocabularyHistoryQuestion, VocabularyPromptCreate


@dataclass
class QuestionWithAnswers:
    questions: List[VocabularyQuestion]
    answers: List[VocabularyAnswer]


def check_language(db: Session, language_name: str) -> int:
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


def parse_question_answers(
    prompt_model: VocabularyPrompt,
    prompt_create: VocabularyPromptCreate,
    learning_language_id: int,
    translated_language_id: int,
) -> QuestionWithAnswers:
    questions = []
    answers = []

    for question in prompt_create.questions:
        vocabulary_question = VocabularyQuestion(
            question_text=question.question_text,
            prompt=prompt_model,
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
    return QuestionWithAnswers(questions=questions, answers=answers)


class VocabularyRepository(
    BaseRepository[VocabularyPrompt, VocabularyPromptCreate, Any]
):
    def create_with_category(
        self,
        prompt_create: VocabularyPromptCreate,
        user_id: str,
    ) -> None:
        with self.session_factory() as session:
            try:
                stmt = (
                    insert(Category)
                    .values(category_name=prompt_create.category, user_id=user_id)
                    .on_conflict_do_update(
                        index_elements=["category_name", "user_id"],
                        set_={"category_name": prompt_create.category},
                    )
                    .returning(Category.id)
                )
                result = session.execute(stmt)
                insert_id = result.fetchone()[0]

                learning_language_id = check_language(
                    session, prompt_create.learning_language
                )
                translated_language_id = check_language(
                    session, prompt_create.translated_language
                )

                prompt_obj = VocabularyPrompt(
                    prompt=prompt_create.prompt,
                    category_id=insert_id,
                    language_id=learning_language_id,
                )

                translated_prompt_obj = VocabularyPromptTranslation(
                    translated_language_id=translated_language_id,
                    translated_text=prompt_create.translation,
                    prompt=prompt_obj,
                )

                session.add(prompt_obj)
                session.add(translated_prompt_obj)

                questions_with_answers = parse_question_answers(
                    prompt_obj,
                    prompt_create,
                    learning_language_id,
                    translated_language_id,
                )

                session.add_all(questions_with_answers.questions)
                session.add_all(questions_with_answers.answers)
                session.commit()
            except SQLAlchemyError as err:
                self.logger.error(err)

    def get_history_questions(
        self, question_input: GetVocabularyHistoryQuestion, user_id: str
    ) -> list[Type[VocabularyPrompt]]:
        with self.session_factory() as session:
            try:
                prompts = (
                    session.query(VocabularyPrompt)
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
                            Category.id == question_input.category_id,
                            Category.user_id == user_id,
                            Language.language_name
                            == question_input.learning_language.upper(),
                            VocabularyPrompt.is_valid,
                        )
                    )
                    .limit(question_input.limit_prompts)
                    .all()
                )
                return prompts
            except SQLAlchemyError as err:
                self.logger.error(err)
            return []
