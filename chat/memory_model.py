"""
UserMemory model — stores persistent facts about a user across all sessions.

Examples of facts stored:
  name        → "Siva"
  profession  → "Software Engineer"
  language    → "Python"
  location    → "xyz city"
  preferences → "Prefers concise answers"
"""
from datetime import datetime
from extensions import db


class UserMemory(db.Model):
    """Persistent per-user memory facts extracted from conversations."""
    __tablename__ = 'user_memories'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, nullable=False, index=True)
    key             = db.Column(db.String(100), nullable=False)   # e.g. "name", "profession"
    value           = db.Column(db.Text,        nullable=False)   # e.g. "Siva"
    source_session  = db.Column(db.Integer, nullable=True)        # session it was learned from
    confidence      = db.Column(db.String(10), default='high')    # high | medium | low
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'key', name='uq_user_memory_key'),
    )

    def to_dict(self):
        return {
            'id':             self.id,
            'user_id':        self.user_id,
            'key':            self.key,
            'value':          self.value,
            'source_session': self.source_session,
            'confidence':     self.confidence,
            'created_at':     self.created_at.isoformat(),
            'updated_at':     self.updated_at.isoformat(),
        }
