from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin


from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    recipes = db.relationship("Recipe", backref = "user")

    serialize_rules = ('-recipes',)

    @property
    def password_hash(self):
        raise AttributeError("Password hash is not accessible.")

    @password_hash.setter
    def password_hash(self, password):
        byte_object = password.encode('utf-8')
        bcrypt_hash = bcrypt.generate_password_hash(byte_object)
        hash_object_as_string = bcrypt_hash.decode('utf-8')
        self._password_hash = hash_object_as_string
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )


    def __repr__(self):
        return f'User {self.username}, ID: {self.id}'



class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (db.CheckConstraint("length(instructions) >= 50"),)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))

    serialize_rules = ('-user',)


    def __repr__(self):
        return f'<Recipe {self.title}, ID: {self.id}>'