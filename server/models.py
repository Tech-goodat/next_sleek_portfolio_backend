from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

metadata=MetaData()

db=SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__="users"

    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String)
    email=db.Column(db.String)
    password=db.Column(db.String)
    description=db.Column(db.String)
    image_url=db.Column(db.String)


    def __repr__(self):
        return f'<User {self.id}, {self.name}, {self.email}, {self.description} , {self.image_url}/>'