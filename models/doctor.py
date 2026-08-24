from extensions import db


class Doctor(db.Model):

    __tablename__ = "doctors"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    specialization = db.Column(
        db.String(100),
        nullable=False
    )

    working_start = db.Column(
        db.String(10),
        nullable=False
    )

    working_end = db.Column(
        db.String(10),
        nullable=False
    )

    slot_duration = db.Column(
        db.Integer,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="doctor_profile"
    )