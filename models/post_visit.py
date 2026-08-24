from extensions import db


class PostVisitRecord(db.Model):

    __tablename__ = "post_visit_records"

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

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    diagnosis = db.Column(
        db.Text,
        nullable=True
    )

    post_visit_notes = db.Column(
        db.Text,
        nullable=False
    )

    prescription = db.Column(
        db.Text,
        nullable=True
    )

    follow_up_instructions = db.Column(
        db.Text,
        nullable=True
    )

    ai_summary = db.Column(
        db.Text,
        nullable=True
    )

    appointment = db.relationship(
        "Appointment",
        backref=db.backref(
            "post_visit_record",
            uselist=False
        )
    )

    doctor = db.relationship(
        "Doctor",
        foreign_keys=[doctor_id]
    )

    patient = db.relationship(
        "User",
        foreign_keys=[patient_id]
    )