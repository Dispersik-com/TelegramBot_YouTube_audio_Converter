from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(12), nullable=False)
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40))
    language = Column(String(2), nullable=True)
    state = Column(String(100))
    previous_state = Column(String(100))
    url = Column(String(150))
    parameters = relationship('Parameters', backref='user')


class Parameters(Base):
    __tablename__ = 'Parameters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    selected_songs = Column(String(150))
    tracklist = relationship('Songs', backref='Parameters')
    sangs_format = Column(String(6))


class Songs(Base):
    __tablename__ = 'Songs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Parameters_id = Column(Integer, ForeignKey('Parameters.id'))
    tracklist_position = Column(Integer())
    timecode = Column(String(10))
    name = Column(String(100))
