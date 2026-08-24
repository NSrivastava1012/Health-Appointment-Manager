from extensions import db


class AISummary(db.Model):

    __tablename__ = "ai_summaries"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=False,
        unique=True
    )

    chief_complaint = db.Column(
        db.Text,
        nullable=False
    )

    key_symptoms = db.Column(
        db.Text,
        nullable=False
    )

    duration = db.Column(
        db.String(100),
        nullable=True
    )

    urgency = db.Column(
        db.String(50),
        nullable=False
    )

    suggested_questions = db.Column(
        db.Text,
        nullable=False
    )

    appointment = db.relationship(
        "Appointment",
        backref="ai_summary"
    )