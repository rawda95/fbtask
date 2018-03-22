from sqlalchemy import Column, ForeignKey, Integer, String, Date,BIGINT
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import database_exists, create_database


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(String(500), primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name

        }


class Post(Base):
    __tablename__ = 'post'

    id = Column(String(500), primary_key=True)
    content = Column(String(500), nullable=True)
    created_time = Column(Date, nullable=False)
    user_id = Column(String(500), ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'content': self.content,
            'date': self.created_time,
            'user_id': self.user_id,

        }


engine = create_engine('postgresql://admin:admin@localhost/v3fbdb')
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)

#sudo -i -u postgres createuser  admin
#ALTER USER admin WITH ENCRYPTED PASSWORD 'admin';

#sudo -u postgres psql -c 'alter user kuser with createdb' postgres
