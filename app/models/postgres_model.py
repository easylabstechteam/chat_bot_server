# ------------------- IMPORTS -------------------
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY  # Use PostgreSQL-specific types
from sqlalchemy.orm import relationship, declarative_base
import uuid  # For generating UUIDs

# ------------------- BASE DECLARATIVE -------------------
Base = declarative_base()  # Base class for all SQLAlchemy models


# ------------------- INTENT MODEL -------------------
class Intent(Base):
    __tablename__ = "intents"  # Table name in the database
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )  # Primary key, auto-generated UUID
    name = Column(Text, unique=True, nullable=False, index=True)  # Name of the intent
    description = Column(Text, nullable=True)  # Optional description
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )  # Creation timestamp

    # Relationship to forms; allows reverse lookup from Intent to its Forms
    forms = relationship(
        "Form",
        back_populates="intent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ------------------- FORM MODEL -------------------
class Form(Base):
    __tablename__ = "forms"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    intent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("intents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(Text, nullable=False)  # Form title
    description = Column(Text, nullable=True)  # Optional description
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    intent = relationship("Intent", back_populates="forms")  # Connect to parent intent
    questions = relationship(
        "Question",
        back_populates="form",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ------------------- QUESTION MODEL -------------------
class Question(Base):
    __tablename__ = "questions"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    form_id = Column(
        UUID(as_uuid=True),
        ForeignKey("forms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text = Column(Text, nullable=False)  # The actual question
    input_type = Column(
        String(20), nullable=False
    )  # Type of input (e.g., text, choice)
    options = Column(ARRAY(Text), nullable=True)  # Options if input_type is 'choice'
    order_index = Column(Integer, nullable=False)  # Ordering of the questions
    is_required = Column(
        Boolean, nullable=False, default=True
    )  # Is this question mandatory?
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    form = relationship("Form", back_populates="questions")  # Link back to form

    __table_args__ = (
        CheckConstraint(
            "order_index > 0", name="check_order_index_positive"
        ),  # Validate positive order_index
    )


# ------------------- CHAT SESSION MODEL -------------------
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    session_token = Column(
        String(128), unique=True, nullable=False, index=True
    )  # Token for session
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Optional user ID
    intent_id = Column(
        UUID(as_uuid=True), ForeignKey("intents.id"), nullable=True, index=True
    )  # Optional intent
    status = Column(
        String(20), nullable=False, default="active"
    )  # Active, completed, etc.
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    intent = relationship("Intent")  # Associated intent
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    answers = relationship(
        "Answer",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    prompts = relationship(
        "LLMPrompt",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ------------------- CHAT MESSAGE MODEL -------------------
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)  # Chat message content
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session = relationship(
        "ChatSession", back_populates="messages"
    )  # Link to parent chat session

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')", name="check_role_valid"
        ),  # Validate role
    )


# ------------------- ANSWER MODEL -------------------
class Answer(Base):
    __tablename__ = "answers"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer = Column(Text, nullable=True)  # The answer content
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship(
        "ChatSession", back_populates="answers"
    )  # Link back to session
    question = relationship("Question")  # Link back to question

    __table_args__ = (
        UniqueConstraint(
            "session_id", "question_id", name="uix_session_question"
        ),  # Prevent duplicate answers
    )


# ------------------- LLM PROMPT LOG MODEL -------------------
class LLMPrompt(Base):
    __tablename__ = "llm_prompts"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prompt = Column(Text, nullable=False)  # Prompt sent to LLM
    response = Column(Text, nullable=False)  # Response from LLM
    tokens_used = Column(Integer, nullable=True)  # Optional token usage tracking
    model_version = Column(String(50), nullable=True)  # Optional model version info
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session = relationship(
        "ChatSession", back_populates="prompts"
    )  # Link to parent session
