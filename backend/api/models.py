from config import db


class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)
    reading_time = db.Column(db.Integer, default=0)
    task_copied = db.Column(db.Boolean, default=False)
    task_viewed = db.Column(db.Boolean, default=False)

    # One-to-Many
    senders = db.relationship('Sender', backref='metric', lazy=True)
    receivers = db.relationship('Receiver', backref='metric', lazy=True)


class Sender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    # user_id belongs to self, not to self.metric.user_id
    user_id = db.Column(db.Integer, nullable=False)


class Receiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    # user_id belongs to self, not to self.metric.user_id
    user_id = db.Column(db.Integer, nullable=False)
