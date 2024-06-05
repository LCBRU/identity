from lbrc_flask.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from sqlalchemy import Boolean, Integer, String, Date
from datetime import date


class CiviCrmStudy(db.Model):
    __tablename__ = 'civicrm_case_type'
    __bind_key__ = 'civicrm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class CiviCrmParticipant(db.Model):
    __tablename__ = 'civicrm_case'
    __bind_key__ = 'civicrm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    study_id: Mapped[int] = mapped_column('case_type_id', Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    study: Mapped[CiviCrmStudy] = relationship(
        CiviCrmStudy,
        foreign_keys=[study_id],
        primaryjoin='CiviCrmStudy.id == CiviCrmParticipant.study_id',
        backref=backref("participants", cascade="delete, delete-orphan")
    )
