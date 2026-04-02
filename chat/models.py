from datetime import datetime
from extensions import db


class ChatSession(db.Model):
    """Persistent chat session per user."""
    __tablename__ = 'chat_sessions'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, nullable=False, index=True)
    title       = db.Column(db.String(255), default='New Chat')
    model       = db.Column(db.String(100), default='')
    is_archived = db.Column(db.Boolean, default=False)
    summary     = db.Column(db.Text, default='') # Condensed conversation history
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_dict(self, include_messages=False):
        data = {
            'id':          self.id,
            'user_id':     self.user_id,
            'title':       self.title,
            'model':       self.model,
            'is_archived': self.is_archived,
            'summary':     self.summary or '',
            'created_at':  self.created_at.isoformat(),
            'updated_at':  self.updated_at.isoformat(),
        }
        if include_messages:
            data['messages'] = [m.to_dict() for m in
                                 self.messages.order_by(ChatMessage.created_at.asc())]
        return data


class ChatMessage(db.Model):
    """Individual chat message stored in SQLite."""
    __tablename__ = 'chat_messages'

    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    role       = db.Column(db.String(20), nullable=False)   # user | assistant | system
    content    = db.Column(db.Text, nullable=False)
    tokens     = db.Column(db.Integer, default=0)           # estimated token count
    is_pinned  = db.Column(db.Boolean, default=False)       # pin important messages
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'session_id': self.session_id,
            'role':       self.role,
            'content':    self.content,
            'tokens':     self.tokens,
            'is_pinned':  self.is_pinned,
            'created_at': self.created_at.isoformat(),
        }
