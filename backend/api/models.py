from config import db, ma


class Metric(db.Model):
    # __tablename__ = 'metric'

    # while constructing new object don't forget to include required key parameters
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)
    reading_time = db.Column(db.Integer, default=0)
    task_copied = db.Column(db.Boolean, default=False)
    task_viewed = db.Column(db.Boolean, default=False)

    # One-to-Many
    senders = db.relationship('Sender', backref='metric', lazy=True)
    receivers = db.relationship('Receiver', backref='metric', lazy=True)

    # Unique pair of (user_id, task_id)
    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='_user_task_uc'), )  # tuple



class Sender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    # user_id belongs to self, not to self.metric.user_id
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'))

    __table_args__ = (db.UniqueConstraint('user_id', 'metric_id', name='_user_metric_uc'), )  # tuple


class Receiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    # user_id belongs to self, not to self.metric.user_id
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'))

    __table_args__ = (db.UniqueConstraint('user_id', 'metric_id', name='_user_metric_uc'), )  # tuple



class MetricSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Metric
        include_fk = True



class SenderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sender
        include_fk = True



class ReceiverSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Receiver
        include_fk = True
