#!/usr/bin/env python3

from flask import request, session, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()

        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in json or not json[field].strip():
                return{'error': f'Missing or empty {field}'}, 422
        
        
        user = User(
            username=json['username'],
            bio=json.get('bio'),
            image_url=json.get('image_url')
        )
        user.password_hash = json['password']
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                return user.to_dict(), 200
        
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return {'error': 'Missing username or password'}, 400

        username = data['username']
        user = User.query.filter(User.username == username).first()

        password = data['password']

        if not user or not user.authenticate(data['password']):
            return {'error': 'Invalid username or password'}, 401

        session['user_id'] = user.id
        return user.to_dict(), 200

class Logout(Resource):
    def delete(self):
        session['user_id'] = None

        return {}, 401

class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'message': 'Unauthorized'}, 401

        recipes = [recipe.to_dict() for recipe in Recipe.query.all()]

        return (recipes), 200

    def post(self):
        if not session.get('user_id'):
            return {'message': 'Unauthorized'}, 401

        json_data = request.get_json()


        title = json_data.get('title')
        instructions = json_data.get('instructions')
        minutes_to_complete = json_data.get('minutes_to_complete')

        if not all(key in json_data for key in ('title', 'instructions', 'minutes_to_complete')):
            return (422, "Missing required fields")

        new_recipe = Recipe(
            title=title,
            instructions = instructions,
            minutes_to_complete = minutes_to_complete,
            user_id=session['user_id']
        )

        try:
            db.session.add(new_recipe)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(422, "Failed to create recipe}")

        return new_recipe.to_dict(), 201




api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)