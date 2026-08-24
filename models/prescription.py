from extensions import db


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=False
    )

    medicine_name = db.Column(
        db.String(150),
        nullable=False
    )

    dosage = db.Column(
        db.String(100)
    )

    frequency = db.Column(
        db.String(100)
    )

    duration = db.Column(
        db.String(100)
    )