from database import db


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


class Analysis(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    job_role = db.Column(
        db.String(100),
        nullable=False
    )

    ats_score = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.now()
    )


class Feedback(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )