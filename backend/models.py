import os
from thirdparty import db, ma

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
    verifications = db.relationship('Verification', backref='metric', lazy=True)

    # Unique pair of (user_id, task_id)
    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='_user_task_uc'), )  # tuple


class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_solution_id = db.Column(db.Integer, nullable=False)
    destination_solution_id = db.Column(db.Integer, nullable=False)

    metric_id = db.Column(db.Integer, db.ForeignKey('metric.id'))

	verdict_of_module = db.Column(db.String, nullable=True)
	verdict_of_human = db.Column(db.Boolean, default=False)

	total_score = db.Column(db.Float, nullable=True)
	text_based_score = db.Column(db.Float, nullable=True)
	tree_based_score = db.Column(db.Float, nullable=True)
	token_based_score = db.Column(db.Float, nullable=True)
	metric_based_score = db.Column(db.Float, nullable=True)
	binary_based_score = db.Column(db.Float, nullable=True)

    __table_args__ = (db.UniqueConstraint('source_solution_id', 'destination_solution_id', name='_source_destination_uc'), )  # tuple


class MetricSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Metric
        include_fk = True

class VerificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Verification
        include_fk = True
