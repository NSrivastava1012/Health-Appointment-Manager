from extensions import db


class DoctorLeave(db.Model):
    __tablename__ = "doctor_leaves"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )

    leave_date = db.Column(
        db.String(20),
        nullable=False
    )

    doctor = db.relationship(
        "Doctor",
        backref="leaves"
    )