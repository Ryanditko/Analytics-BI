from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    agent_id = Column(String, index=True)
    queue_id = Column(String, index=True)
    channel_type = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # em segundos
    wait_time = Column(Integer)  # em segundos
    talk_time = Column(Integer)  # em segundos
    status = Column(String)
    reason = Column(String, nullable=True)
    is_auto_service = Column(Boolean, default=False)
    auto_service_type = Column(String, nullable=True)
    is_callback = Column(Boolean, default=False)
    callback_reason = Column(String, nullable=True)
    is_duplicate_channel = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CSAT(Base):
    __tablename__ = "csat_scores"
    
    id = Column(Integer, primary_key=True)
    interaction_id = Column(String, ForeignKey("interactions.id"))
    agent_id = Column(String, index=True)
    customer_id = Column(String, index=True)
    score = Column(Integer)
    clarity_score = Column(Integer)
    wait_time_score = Column(Integer)
    navigation_score = Column(Integer)
    open_feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HSM(Base):
    __tablename__ = "hsm_messages"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    agent_id = Column(String, index=True)
    template_id = Column(String)
    message = Column(String)
    status = Column(String)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String, nullable=True)
    is_mass_message = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SpeechAnalytics(Base):
    __tablename__ = "speech_analytics"
    
    id = Column(Integer, primary_key=True)
    interaction_id = Column(String, ForeignKey("interactions.id"))
    topic = Column(String)
    confidence = Column(Float)
    transcript = Column(String)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentMetrics(Base):
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String, index=True)
    date = Column(DateTime, index=True)
    total_interactions = Column(Integer)
    answered_interactions = Column(Integer)
    average_handle_time = Column(Float)
    average_wait_time = Column(Float)
    average_talk_time = Column(Float)
    service_level = Column(Float)
    csat_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class QueueMetrics(Base):
    __tablename__ = "queue_metrics"
    
    id = Column(Integer, primary_key=True)
    queue_id = Column(String, index=True)
    date = Column(DateTime, index=True)
    total_interactions = Column(Integer)
    answered_interactions = Column(Integer)
    abandoned_interactions = Column(Integer)
    average_wait_time = Column(Float)
    service_level = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow) 