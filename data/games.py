import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Game(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    group_id = sqlalchemy.Column(sqlalchemy.Integer)
    x = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    time_per_round = sqlalchemy.Column(sqlalchemy.Integer)
    lucky_number = sqlalchemy.Column(sqlalchemy.Integer, default=-1)
    limit_retired = sqlalchemy.Column(sqlalchemy.Integer)
    current_retired = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    current_alives = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    status = sqlalchemy.Column(sqlalchemy.String, default='inactive')
    members = orm.relationship('Member', backref='game')


    def set_x(self) -> None:
        self.x = len(self.members) - self.current_retired - 1

    def check_number(self, chosen_number: int) -> bool:
        for member in self.members:
            try:
                number = int(member.chosen_number)
                if number == chosen_number:
                    return False
            except ValueError:
                pass
        return True
