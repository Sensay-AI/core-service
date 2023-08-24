from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.infrastructure.db.database import Base

FOREIGN_LANGUAGE_ID = "languages.id"
FOREIGN_VOCA_QUESTION_ID = "vocabulary_questions.id"
FOREIGN_VOCA_ANSWER_ID = "vocabulary_answers.id"


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("user_info.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prompts = relationship("VocabularyPrompt", back_populates="category")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "category_name", name="uq_category_user_id_category_name"
        ),
    )


class VocabularyPrompt(Base):
    __tablename__ = "vocabulary_prompts"
    id = Column(Integer, primary_key=True)
    prompt = Column(String, nullable=False)
    level = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_valid = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    language_id = Column(Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False)
    language = relationship("Language")
    questions = relationship("VocabularyQuestion", back_populates="prompt")
    category = relationship("Category", back_populates="prompts")
    translations = relationship("VocabularyPromptTranslation", back_populates="prompt")


class VocabularyQuestion(Base):
    __tablename__ = "vocabulary_questions"
    id = Column(Integer, primary_key=True)
    question_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_valid = Column(Boolean, default=True)

    answers = relationship("VocabularyAnswer", back_populates="question")
    prompt = relationship("VocabularyPrompt", back_populates="questions")
    prompt_id = Column(Integer, ForeignKey("vocabulary_prompts.id"), nullable=False)
    language_id = Column(Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False)
    translations = relationship(
        "VocabularyQuestionTranslation", back_populates="question"
    )


class VocabularyAnswer(Base):
    __tablename__ = "vocabulary_answers"
    id = Column(Integer, primary_key=True)
    answer_text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    question_id = Column(Integer, ForeignKey(FOREIGN_VOCA_QUESTION_ID), nullable=False)
    language_id = Column(Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False)
    question = relationship("VocabularyQuestion", back_populates="answers")
    translations = relationship("VocabularyAnswerTranslation", back_populates="answer")


class ChoiceQuestionResponse(Base):
    __tablename__ = "choice_question_response"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey(FOREIGN_VOCA_QUESTION_ID))
    answer_selected_id = Column(Integer, ForeignKey(FOREIGN_VOCA_ANSWER_ID))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("user_info.id"))


class VocabularyPromptTranslation(Base):
    __tablename__ = "vocabulary_prompt_translations"
    id = Column(Integer, primary_key=True)
    translated_language_id = Column(
        Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False
    )
    translated_text = Column(String)
    prompt_id = Column(Integer, ForeignKey("vocabulary_prompts.id"), nullable=False)
    prompt = relationship("VocabularyPrompt", back_populates="translations")
    translated_language = relationship("Language")


class VocabularyQuestionTranslation(Base):
    __tablename__ = "vocabulary_question_translations"
    id = Column(Integer, primary_key=True)
    translated_text = Column(String)
    translated_language_id = Column(
        Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False
    )
    question_id = Column(Integer, ForeignKey(FOREIGN_VOCA_QUESTION_ID), nullable=False)
    question = relationship("VocabularyQuestion", back_populates="translations")
    translated_language = relationship("Language")


class VocabularyAnswerTranslation(Base):
    __tablename__ = "vocabulary_answer_translations"
    id = Column(Integer, primary_key=True)
    translated_text = Column(String)
    translated_language_id = Column(
        Integer, ForeignKey(FOREIGN_LANGUAGE_ID), nullable=False
    )
    answer_id = Column(Integer, ForeignKey(FOREIGN_VOCA_ANSWER_ID), nullable=False)
    answer = relationship("VocabularyAnswer", back_populates="translations")
    translated_language = relationship("Language")
