# Import core SQLAlchemy components for defining database models
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, JSON, Index
from sqlalchemy.orm import relationship, declarative_base

# Import PostgreSQL-specific UUID type for unique identifiers
from sqlalchemy.dialects.postgresql import UUID

# Standard Python modules for handling dates and generating unique IDs
from datetime import datetime
import uuid

# Import async engine creation for non-blocking database operations
from sqlalchemy.ext.asyncio import create_async_engine

# Import declarative_base to create the base class for all models
from sqlalchemy.orm import declarative_base

# Import your database URL from your configuration
from core.config import DATABASE_URL

# Create an asynchronous engine to connect to the database
# echo=True logs all SQL statements to the console (useful for debugging)
engine = create_async_engine(DATABASE_URL, echo=True)

# Base class for all database models
# Every model you define will inherit from this, so SQLAlchemy knows it's part of the database
Base = declarative_base()

# Function to initialize all database tables
# This will create all tables in PostgreSQL if they don't already exist
async def init_models():
    # Open a connection to the database
    async with engine.begin() as conn:
        # Create all tables defined by models inheriting from Base
        await conn.run_sync(Base.metadata.create_all)


# ------------------- CHAT USERS -------------------
class ChatUser(Base):
    # Represents a visitor chatting with the bot.
    # Can have multiple sessions, messages, contexts, feedbacks, and lead status.

    __tablename__ = "chat_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique user ID
    ip_address = Column(String(45), nullable=True)  # Optional IP address
    name = Column(String(100), nullable=False)  # User's name
    email = Column(String(255), unique=True, nullable=True)  # Optional email
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp

    # Relationships to access related data easily
    sessions = relationship("Session", back_populates="chat_user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chat_user", cascade="all, delete-orphan")
    analytics_records = relationship("AnalyticsRecord", back_populates="chat_user", cascade="all, delete-orphan")
    contexts = relationship("ConversationContext", back_populates="chat_user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="chat_user", cascade="all, delete-orphan")
    high_potential_leads = relationship("HighPotentialLead", back_populates="chat_user", cascade="all, delete-orphan")
    no_potential_leads = relationship("NoPotentialLead", back_populates="chat_user", cascade="all, delete-orphan")


Index('idx_chat_users_email', ChatUser.email)  # Fast lookup by email


# ------------------- ADMIN USERS -------------------
class AdminUser(Base):
    # Represents admin users who can manage the system.

    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)  # Login name
    password_hash = Column(String(255), nullable=False)  # Secure password hash
    role = Column(String(50), default="admin")  # Role type
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ------------------- SESSIONS -------------------
class Session(Base):
    # Represents a single conversation with a user.
    # Contains messages, context, analytics, and prompt history.

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_user_id = Column(UUID(as_uuid=True), ForeignKey("chat_users.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)  # Session start time
    ended_at = Column(DateTime, nullable=True)  # Optional end time
    session_metadata = Column(JSON, nullable=True)  # Extra info about session

    chat_user = relationship("ChatUser", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    analytics_records = relationship("AnalyticsRecord", back_populates="session", cascade="all, delete-orphan")
    contexts = relationship("ConversationContext", back_populates="session", cascade="all, delete-orphan")
    prompt_histories = relationship("PromptHistory", back_populates="session", cascade="all, delete-orphan")


Index('idx_sessions_user', Session.chat_user_id)  # Fast lookup of sessions by user


# ------------------- INTENTS -------------------
class Intent(Base):
    # Represents the purpose of a message or question (e.g., "greeting", "purchase inquiry").

    __tablename__ = "intents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)  # Name of the intent
    description = Column(Text, nullable=True)  # Optional description
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="intent")
    questions = relationship("Question", back_populates="intent")
    system_prompts = relationship("SystemPrompt", back_populates="intent")
    analytics_records = relationship("AnalyticsRecord", back_populates="intent")
    high_potential_leads = relationship("HighPotentialLead", back_populates="intent")
    no_potential_leads = relationship("NoPotentialLead", back_populates="intent")


Index('idx_intents_name', Intent.name)  # Fast lookup by intent name


# ------------------- MESSAGES -------------------
class Message(Base):
    # Represents a single message in a session.
    # Can be from the user, bot, or admin.

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    chat_user_id = Column(UUID(as_uuid=True), ForeignKey("chat_users.id", ondelete="SET NULL"), nullable=True)  # Null for bot messages
    role = Column(String(10), nullable=False)  # "user", "bot", or "admin"
    intent_id = Column(UUID(as_uuid=True), ForeignKey("intents.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)  # Message text
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")
    chat_user = relationship("ChatUser", back_populates="messages")
    intent = relationship("Intent", back_populates="messages")
    analytics_records = relationship("AnalyticsRecord", back_populates="message", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="message", cascade="all, delete-orphan")
    prompt_histories = relationship("PromptHistory", back_populates="message", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")


Index('idx_messages_session', Message.session_id)
Index('idx_messages_user', Message.chat_user_id)


# ------------------- QUESTIONS -------------------
class Question(Base):
    # Predefined questions the bot asks, linked to intents.

    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)  # Question text
    intent_id = Column(UUID(as_uuid=True), ForeignKey("intents.id", ondelete="CASCADE"), nullable=False)
    question_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    intent = relationship("Intent", back_populates="questions")


# ------------------- SYSTEM PROMPTS -------------------
class SystemPrompt(Base):
    # Prompts to guide the LLM based on intent.

    __tablename__ = "system_prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)  # Prompt content
    intent_id = Column(UUID(as_uuid=True), ForeignKey("intents.id", ondelete="CASCADE"), nullable=False)
    system_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("Intent", back_populates="system_prompts")


# ------------------- ANALYTICS METRICS ------------------- 
class AnalyticsMetric(Base):
    # Defines the type of metric we are tracking.

    __tablename__ = "analytics_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)  # Metric name
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analytics_records = relationship("AnalyticsRecord", back_populates="analytics_metric", cascade="all, delete-orphan")


# ------------------- ANALYTICS RECORDS -------------------
class AnalyticsRecord(Base):
    # Stores values for metrics (e.g., messages sent, response time).

    __tablename__ = "analytics_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analytics_metric_id = Column(UUID(as_uuid=True), ForeignKey("analytics_metrics.id", ondelete="CASCADE"), nullable=False)
    chat_user_id = Column(UUID(as_uuid=True), ForeignKey("chat_users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    intent_id = Column(UUID(as_uuid=True), ForeignKey("intents.id", ondelete="SET NULL"), nullable=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    metric_value = Column(Float, nullable=False)  # Numeric value
    recorded_at = Column(DateTime, default=datetime.utcnow)

    analytics_metric = relationship("AnalyticsMetric", back_populates="analytics_records")
    chat_user = relationship("ChatUser", back_populates="analytics_records")
    session = relationship("Session", back_populates="analytics_records")
    intent = relationship("Intent", back_populates="analytics_records")
    message = relationship("Message", back_populates="analytics_records")

# ------------------- CONVERSATION CONTEXT -------------------
class ConversationContext(Base):
    # Stores session-level memory or context for multi-turn conversations.

    __tablename__ = "conversation_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    chat_user_id = Column(UUID(as_uuid=True), ForeignKey("chat_users.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)  # Context key name
    value = Column(Text, nullable=False)  # Context value
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="contexts")
    chat_user = relationship("ChatUser", back_populates="contexts")


# ------------------- EMBEDDINGS -------------------
class Embedding(Base):
    
    # Stores vector embeddings for messages (for semantic search or RAG).

    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)
    vector = Column(JSON, nullable=False)  # Embedding vector
    embedding_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="embeddings")


# ------------------- PROMPT HISTORY -------------------
class PromptHistory(Base):
    # Stores prompts sent to the LLM for traceability.

    __tablename__ = "prompt_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)
    prompt_text = Column(Text, nullable=False)
    prompt_history_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="prompt_histories")
    message = relationship("Message", back_populates="prompt_histories")


# ------------------- FEEDBACK -------------------
class Feedback(Base):
    # Stores user feedback on messages or sessions.

    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_user_id = Column(UUID(as_uuid=True), ForeignKey("chat_users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, nullable=True)  # e.g., 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat_user = relationship("ChatUser", back_populates="feedbacks")
    message = relationship("Message", back_populates="feedbacks")


# ------------------- HIGH POTENTIAL LEADS -------------------
class HighPotentialLead(Base):
    # Stores users flagged as high-potential leads by the LLM or rules.

    __tablename__ = "high_potential_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_user_id = Column(UUID(as_uuid=True), ForeignKey("chat_users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_ids = Column(JSON, nullable=True)  # List of message IDs contributing to this lead
    intent_id = Column(UUID(as_uuid=True), ForeignKey("intents.id", ondelete="SET NULL"), nullable=True)
    lead_score = Column(Float, default=0.0)  # Score indicating likelihood of lead
    status = Column(String(50), default="new")  # new, notified, contacted
    high_potential_lead_metadata = Column(JSON, nullable=True)  # Extra info like email sent, tags
    detected_at = Column(DateTime, default=datetime.utcnow)

    chat_user = relationship("ChatUser", back_populates="high_potential_leads")
    session = relationship("Session", back_populates="high_potential_leads")
    intent = relationship("Intent", back_populates="high_potential_leads")


# ------------------- NO POTENTIAL LEADS -------------------
class NoPotentialLead(Base):
    # Stores users evaluated but NOT flagged as high-potential leads.

    __tablename__ = "no_potential_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_user_id = Column(UUID(as_uuid=True), ForeignKey("chat_users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_ids = Column(JSON, nullable=True)
    intent_id = Column(UUID(as_uuid=True), ForeignKey("intents.id", ondelete="SET NULL"), nullable=True)
    no_potential_lead_metadata = Column(JSON, nullable=True)  # Optional notes or reasons
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    chat_user = relationship("ChatUser", back_populates="no_potential_leads")
    session = relationship("Session", back_populates="no_potential_leads")
    intent = relationship("Intent", back_populates="no_potential_leads")
