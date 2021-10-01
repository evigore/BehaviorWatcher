import os
import json
from Thirdparty import db, ma
from dataclasses import dataclass

class Metric(db.Model):
    # __tablename__ = 'metric'

    # while constructing new object don't forget to include required key parameters
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)
    reading_time = db.Column(db.Integer, server_default=db.text('0'))
    task_copied = db.Column(db.Boolean, server_default=db.false())
    task_viewed = db.Column(db.Boolean, server_default=db.false())

    # Unique pair of (user_id, task_id)
    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='_user_task_uc'), )  # tuple


class Verification(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	source_solution_id = db.Column(db.Integer, nullable=False)
	destination_solution_id = db.Column(db.Integer, nullable=False)

	source_user_id = db.Column(db.Integer, nullable=False)
	destination_user_id = db.Column(db.Integer, nullable=False)
	task_id = db.Column(db.Integer, nullable=False)

	verdict_of_module = db.Column(db.String, nullable=True)
	verdict_of_human = db.Column(db.Boolean, server_default=db.false())

	total_score = db.Column(db.Float, nullable=True)
	text_based_score = db.Column(db.Float, nullable=True)
	tree_based_score = db.Column(db.Float, nullable=True)
	token_based_score = db.Column(db.Float, nullable=True)
	metric_based_score = db.Column(db.Float, nullable=True)
	binary_based_score = db.Column(db.Float, nullable=True)

	__table_args__ = (db.UniqueConstraint('source_solution_id', 'destination_solution_id', name='_source_destination_uc'), )  # tuple


@dataclass
class Error:
    message: str

class ErrorSchema(ma.Schema):
    message = ma.Str()


class MetricSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Metric
        include_fk = True

class VerificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Verification
        include_fk = True
