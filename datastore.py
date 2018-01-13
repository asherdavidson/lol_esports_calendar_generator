from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker, relationship

DB_FILE_NAME = 'datastore.db'

engine = create_engine('sqlite:///{}'.format(DB_FILE_NAME), echo=False, connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@as_declarative()
class Base(object):
    def __repr__(self):
        cls = type(self)
        column_names = [c.name for c in cls.__table__.columns]
        column_values = [repr(getattr(self, column_name)) for column_name in column_names]

        params_str = ""
        for i in range(len(column_names)):
            params_str += "{}={}, ".format(column_names[i], column_values[i])
        params_str = params_str[:-2]

        return "{}({})".format(cls.__name__,
                               params_str)

    @classmethod
    def create_or_update(cls, session, id, **new_fields):
        column_names = [c.name for c in cls.__table__.columns]

        obj = session.query(cls).filter(cls.id == id).one_or_none()

        if obj:
            for column_name, new_value in new_fields.items():
                if column_name in column_names:
                    setattr(obj, column_name, new_value)
        else:
            obj = cls(id=id, **new_fields)

        session.add(obj)

        return obj


class League(Base):
    __tablename__ = 'leagues'

    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True)
    name = Column(String, unique=True)
    region = Column(String)
    logo_url = Column(String)

    tournaments = relationship('Tournament', order_by='Tournament.id', back_populates='league')
    brackets = relationship('Bracket', order_by='Bracket.id', back_populates='league')
    matches = relationship('Match', order_by='Match.id', back_populates='league')


class Tournament(Base):
    __tablename__ = 'tournaments'

    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)

    league_id = Column(Integer, ForeignKey('leagues.id'))
    league = relationship('League', back_populates='tournaments')

    brackets = relationship('Bracket', order_by='Bracket.id', back_populates='tournament')
    rosters = relationship('Roster', order_by='Roster.id', back_populates='tournament')
    matches = relationship('Match', order_by='Match.id', back_populates='tournament')


class Bracket(Base):
    __tablename__ = 'brackets'

    id = Column(String, primary_key=True)
    name = Column(String)

    position = Column(Integer)
    group_position = Column(Integer)
    group_name = Column(String)

    tournament_id = Column(String, ForeignKey('tournaments.id'))
    tournament = relationship('Tournament', back_populates='brackets')

    league_id = Column(String, ForeignKey('leagues.id'))
    league = relationship('League', back_populates='brackets')

    matches = relationship('Match', order_by='Match.id', back_populates='bracket')


class Match(Base):
    __tablename__ = 'matches'

    id = Column(String, primary_key=True)
    name = Column(String)
    scheduled_time = Column(DateTime(timezone=True))
    num_matches = Column(Integer)

    position = Column(Integer)
    group_position = Column(Integer)

    block_label = Column(String)
    sub_block_label = Column(String)
    block_prefix = Column(String)
    sub_block_prefix = Column(String)

    league_id = Column(Integer, ForeignKey('leagues.id'))
    league = relationship('League', back_populates='matches')

    tournament_id = Column(String, ForeignKey('tournaments.id'))
    tournament = relationship('Tournament', back_populates='matches')

    bracket_id = Column(String, ForeignKey('brackets.id'))
    bracket = relationship('Bracket', back_populates='matches')

    team_a_id = Column(Integer, ForeignKey('teams.id'))
    team_a = relationship('Team', foreign_keys=[team_a_id])

    team_b_id = Column(Integer, ForeignKey('teams.id'))
    team_b = relationship('Team', foreign_keys=[team_b_id])

    roster_a_id = Column(String, ForeignKey('rosters.id'))
    roster_a = relationship('Roster', foreign_keys=[roster_a_id])

    roster_b_id = Column(String, ForeignKey('rosters.id'))
    roster_b = relationship('Roster', foreign_keys=[roster_b_id])


class Roster(Base):
    __tablename__ = 'rosters'

    id = Column(String, primary_key=True)
    name = Column(String)

    tournament_id = Column(String, ForeignKey('tournaments.id'))
    tournament = relationship('Tournament', back_populates='rosters')

    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship('Team', back_populates='rosters')


class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    slug = Column(String)
    name = Column(String)
    acronym = Column(String, unique=True)

    rosters = relationship('Roster', back_populates='team')


def create_tables():
    Base.metadata.create_all(engine)


def clear_tables():
    Base.metadata.drop_all(engine)
