from extensions import db


class Symptom(db.Model):

    __tablename__ = "symptoms"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=False
    )

    symptoms_text = db.Column(
        db.Text,
        nullable=False
    )

    appointment = db.relationship(
        "Appointment",
        backref="symptom"
    )