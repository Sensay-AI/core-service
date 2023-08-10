import enum

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

from app.db.database import Base


class TypeText(enum.Enum):
    vocabularyPrompt = 0
    vocabularyQuestion = 1
    vocabularyAnswer = 2


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("user_info.user_id"), nullable=False)

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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_valid = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    questions = relationship("VocabularyQuestion", back_populates="prompt")
    category = relationship("Category", back_populates="prompts")


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
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)


class VocabularyAnswer(Base):
    __tablename__ = "vocabulary_answers"
    id = Column(Integer, primary_key=True)
    answer_text = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    question_id = Column(Integer, ForeignKey("vocabulary_questions.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    question = relationship("VocabularyQuestion", back_populates="answers")


class ChoiceQuestionResponse(Base):
    __tablename__ = "choice_question_response"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("vocabulary_questions.id"))
    answer_selected_id = Column(Integer, ForeignKey("vocabulary_answers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("user_info.id"))


# class TranslationText(Base):
#     __tablename__ = "translation_texts"
#     id = Column(Integer, primary_key=True)
#     translated_text = Column(String, nullable=False)
#     language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
#     type_text = Column(Enum(TypeText), nullable=False)
#     primary_text_id = Column(Integer, nullable=False)
#
#     vocabulary_prompt = relationship(
#         "VocabularyPrompt",
#         primaryjoin=f"and_(VocabularyPrompt.id==TranslationText.primary_text_id, TranslationText.type_text=={TypeText.vocabularyPrompt.value})",
#     )
#     vocabulary_question = relationship(
#         "VocabularyQuestion",
#         primaryjoin=f"and_(VocabularyQuestion.id==TranslationText.primary_text_id, TranslationText.type_text=={TypeText.vocabularyQuestion.value})",
#     )
#     vocabulary_answer = relationship(
#         "VocabularyAnswer",
#         primaryjoin=f"and_(VocabularyAnswer.id==TranslationText.primary_text_id, TranslationText.type_text=={TypeText.vocabularyAnswer.value})",
#     )
