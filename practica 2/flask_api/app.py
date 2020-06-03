from flask import Flask, render_template
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
from db import db
from flask_migrate import Migrate
from models.artist import ArtistModel
from models.event import EventModel
from models.account import AccountsModel
from models.order import OrdersModel
from flask_httpauth import HTTPBasicAuth
from flask import g
from decouple import config as config_decouple
from config import config

app = Flask(__name__)
environment = config['development']
if config_decouple('PRODUCTION', cast=bool, default=False):
    environment = config['production']

app.config.from_object(environment)

CORS(app, resources={r'/*': {'origins': '*'}})

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(token, password):
    user = AccountsModel.verify_auth_token(token)
    if user:
        g.user = user
        return user

    return None

@auth.get_user_roles
def get_user_roles(user):
    if user.is_admin == 1:
        return ['admin']
    else:
        return ['user']


class Artist(Resource):

    def get(self, id):
        artist = ArtistModel.query.filter_by(id=id).first()
        if(artist):
            return artist.json(), 200
        return {'message': 'Artist not found'}, 404

    @auth.login_required(role='admin')
    def post(self):

        parser = reqparse.RequestParser()  # create parameters parser from request

        # define al input parameters need and its type
        parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('country', type=str)
        parser.add_argument('genre', type=str)

        data = parser.parse_args()

        for artist in ArtistModel.query.all():
            if(data['name'] == artist.name):
                return {'message': 'Artist {} already exists'.format(artist.name)}, 404

        new_artist = ArtistModel(data['name'], data['country'], data['genre'])

        new_artist.save_to_db()

        return new_artist.json(), 200

    @auth.login_required(role='admin')
    def delete(self, id):

        artist = ArtistModel.query.filter_by(id=id).first()

        if not artist:
            return {'message': "Artist not found, can't be deleted"}, 404

        events = EventModel.query.all()
        for event in events:
            for artist_query in event.artists:
                if artist.id == artist_query.id:
                    event.artists.remove(artist)

        artist.delete_from_db()
        return artist.json(), 200

    @auth.login_required(role='admin')
    def put(self):
        parser = reqparse.RequestParser()  # create parameters parser from request

        # define al input parameters need and its type
        parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('new_name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('country', type=str)
        parser.add_argument('genre', type=str)

        data = parser.parse_args()

        artist = ArtistModel.query.filter_by(name=data['name']).first()

        if artist:
            artist.name = data['new_name']
            artist.country = data['country']
            artist.genre = data['genre']
            artist.save_to_db()
            return artist.json(), 200

        return {'message': 'Artist not found'}, 404


class Event(Resource):

    def get(self, id):
        event = EventModel.query.filter_by(id=id).first()
        if (event):
            return event.json(), 200
        return {'message': 'Artist not found'}, 404

    @auth.login_required(role='admin')
    def post(self):

        parser = reqparse.RequestParser()  # create parameters parser from request

        # define al input parameters need and its type
        parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('place', type=str)
        parser.add_argument('city', type=str)
        parser.add_argument('date', type=str)
        parser.add_argument('price', type=int)
        parser.add_argument('total_available_tickets', type=int)


        data = parser.parse_args()

        for event in EventModel.query.all():
            if (data['name'] == event.name):
                return {'message': 'Event {} already exists'.format(event.name)}, 404

        new_event = EventModel(data['name'], data['place'], data['city'], data['date'], data['price'], data['total_available_tickets'])

        new_event.save_to_db()

        return new_event.json(), 200

    @auth.login_required(role='admin')
    def delete(self, id):
        event = EventModel.query.filter_by(id=id).first()

        if not event:
            return {'message': "Event not found, can't be deleted"}, 404

        orders = OrdersModel.query.all()
        for order in orders:
            if order.id_event == event.id:
                order.delete_from_db()

        event.delete_from_db()
        return event.json(), 200

    @auth.login_required(role='admin')
    def put(self, id):
        parser = reqparse.RequestParser()  # create parameters parser from request

        # define al input parameters need and its type
        parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('place', type=str)
        parser.add_argument('city', type=str)
        parser.add_argument('date', type=str)
        parser.add_argument('price', type=int)
        parser.add_argument('total_available_tickets', type=int)

        data = parser.parse_args()

        event = EventModel.query.filter_by(id=id).first()
        if (event):
            event.name = data['name']
            event.place = data['place']
            event.city = data['city']
            event.date = data['date']
            event.price = data['price']
            event.total_available_tickets = data['total_available_tickets']
            event.save_to_db()
            return event.json(), 200

        return {'message': 'Artist not found'}, 404


class ArtistList(Resource):

    def get(self):
        artistList = []
        artists = ArtistModel.query.all()
        for artist in artists:
            artistList.append(artist.json())
        return {'artists': artistList}

    def post(self, id):
        return {'message': "Not developed yet"}, 404

    def delete(self,id):
        return {'message': "Not developed yet"}, 404

    def put(self,id):
        return {'message': "Not developed yet"}, 404


class EventList(Resource):

    def get(self):
        eventList = []
        events = EventModel.query.all()
        for artist in events:
            eventList.append(artist.json())
        return {'events': eventList}

    def post(self):
        return {'message': "Not developed yet"}, 404

    def delete(self,id):
        return {'message': "Not developed yet"}, 404

    def put(self,id):
        return {'message': "Not developed yet"}, 404


class EventArtistsList(Resource):

    def get(self, id):
        artistList = []
        event = EventModel.query.filter_by(id=id).first()
        if(event):
            for artist in event.artists:
                artistList.append(artist.json())
            return {'artists': artistList}

        return {'message': 'Event not found'}, 404


    def post(self, id):
        return {'message': "Not developed yet"}, 404

    def delete(self,id):
        return {'message': "Not developed yet"}, 404

    def put(self,id):
        return {'message': "Not developed yet"}, 404


class EventArtist(Resource):

    def get(self, id_event, id_artist):
        event = EventModel.query.filter_by(id=id_event).first()

        if not event:
            return {'message': 'Event not found'}, 404

        for artist in event.artists:
            if(artist.id == id_artist):
                return artist.json(), 200

        return {'message': "Artist not found"}, 404

    @auth.login_required(role='admin')
    def post(self, id_event):

        event = EventModel.query.filter_by(id=id_event).first()
        if not event:
            return {'message': 'Event not found'}, 404

        parser = reqparse.RequestParser()  # create parameters parser from request

        # define al input parameters need and its type
        parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('country', type=str)
        parser.add_argument('genre', type=str)

        data = parser.parse_args()

        # Si existeix, l'afegim a la llista d'artistes de l'event
        for artist in ArtistModel.query.all():
            if (data['name'] == artist.name):
                event.artists.append(artist)
                db.session.commit()
                return {'artist': artist.json()}, 200

        # Si no, el creem i l'afegim a la llista d'artistes de l'event
        new_artist = ArtistModel(data['name'], data['country'], data['genre'])
        event.artists.append(new_artist)
        new_artist.save_to_db()

        return new_artist.json(), 200

    @auth.login_required(role='admin')
    def delete(self, id_event, id_artist):

        event = EventModel.query.filter_by(id=id_event).first()
        if not event:
            return {'message': 'Event not found'}, 404

        artist = ArtistModel.query.filter_by(id=id_artist).first()

        for a in event.artists:
            if artist.name == a.name:
                event.artists.remove(artist)
                db.session.commit()
                return {'event': event.json()}, 200

        return {'message': 'Artist not found'}, 404

    def put(self, id):
        return {'message': "Not developed yet"}, 404

class ArtistEventsList(Resource):

    def get(self, id):
        eventsList = []
        artist = ArtistModel.query.filter_by(id=id).first()
        if not artist:
            return {'message': 'Artist not found'}, 404

        for event in EventModel.query.all():
            for eventartist in event.artists:
                if eventartist.id == artist.id:
                    eventsList.append(event)

        return {'events': [event.json() for event in eventsList]}, 200

    def post(self, id):
        return {'message': "Not developed yet"}, 404

    def delete(self,id):
        return {'message': "Not developed yet"}, 404

    def put(self,id):
        return {'message': "Not developed yet"}, 404


class Orders(Resource):

    def get(self, username):
        orders = []
        user = AccountsModel.query.filter_by(username=username).first()
        if not user:
            return {'message': 'User not found'}, 404

        for order in OrdersModel.query.all():
            if order.username == username:
                orders.append(order.json())

        return {'orders': orders}, 200

    @auth.login_required()
    def post(self, username):

        parser = reqparse.RequestParser()  # create parameters parser from request+

        # define al input parameters need and its type
        parser.add_argument('id_event', type=int, required=True, help="This field cannot be left blank")
        parser.add_argument('tickets_bought', type=int, required=True, help="This field cannot be left blank")

        data = parser.parse_args()

        user = AccountsModel.query.filter_by(username=username).first()
        event = EventModel.query.filter_by(id=data['id_event']).first()

        if username != g.user.username:
            return {'message': 'Bad authorization user'}, 401

        if not user:
            return {'message': 'User not found'}, 404

        if not event:
            return {'message': 'Event not found'}, 404

        if(user.available_money < data['tickets_bought'] * event.price):
            return {'message': 'Not enough money'}, 400

        if(event.total_available_tickets < data['tickets_bought']):
            return {'message': 'Not enough tickets available'}, 400

        event.total_available_tickets -= data['tickets_bought']
        user.available_money -= data['tickets_bought'] * event.price
        user.save_to_db()
        print(user.available_money)

        new_order = OrdersModel(data['id_event'], data['tickets_bought'])
        user.orders.append(new_order)
        user.save_to_db()

        return {'order': new_order.json()}, 200

    def delete(self):
        return {'message': "Not developed yet"}, 404

    def put(self):
        return {'message': "Not developed yet"}, 404


class OrdersList(Resource):

    def get(self):
        orders = []
        for order in OrdersModel.query.all():
            orders.append(order.json())

        return {'orders': orders}, 200

    def post(self, id):
        return {'message': "Not developed yet"}, 404

    @auth.login_required(role='admin')
    def delete(self):
        OrdersModel.query.delete()

        users = AccountsModel.query.all()
        for user in users:
            user.orders = []

        return {'message': "All orders erased successfully"}, 200

    def put(self,id):
        return {'message': "Not developed yet"}, 404


class Accounts(Resource):

    def get(self, username):
        user = AccountsModel.query.filter_by(username=username).first()

        if not user:
            return {'message': 'User not found'}, 404

        return user.json(), 200

    def post(self):

        parser = reqparse.RequestParser()  # create parameters parser from request+

        # define al input parameters need and its type
        parser.add_argument('username', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('password', type=str, required=True, help="This field cannot be left blank")

        data = parser.parse_args()

        user = AccountsModel.query.filter_by(username=data['username']).first()

        if user:
            return {'message': 'Username already exists'}, 404

        new_user = AccountsModel(data['username'])
        token = new_user.generate_auth_token()
        new_user.hash_password(data['password'])
        new_user.save_to_db()

        return {'token': token.decode('ascii')}, 200

    @auth.login_required(role='admin')
    def delete(self, username):
        user = AccountsModel.query.filter_by(username=username).first()

        if not user:
            return {'message': 'User not found'}, 404

        orders = OrdersModel.query.all()
        for order in orders:
            if order.username == username:
                orders.remove(order)

        user = AccountsModel.query.filter_by(username=username).delete()

        return {'message': "User {} successfully deleted.".format(username)}, 200

    def put(self,id):
        return {'message': "Not developed yet"}, 404


class AccountsList(Resource):

    def get(self):
        accounts = AccountsModel.query.all()

        return {'accounts': [account.json() for account in accounts]}, 200

    def post(self, id):
        return {'message': "Not developed yet"}, 404

    @auth.login_required(role='admin')
    def delete(self,id):
        return {'message': "Not developed yet"}, 404

    def put(self,id):
        return {'message': "Not developed yet"}, 404


class Login(Resource):

    def get(self, username, password):
        return {'message': 'Not implemented yet'}, 404


    def post(self):

        parser = reqparse.RequestParser()  # create parameters parser from request+

        # define al input parameters need and its type
        parser.add_argument('username', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('password', type=str, required=True, help="This field cannot be left blank")

        data = parser.parse_args()

        users = AccountsModel.query.all()

        for user in users:
            if user.username == data['username']:
                if(user.verify_password(data['password'])):
                    token = user.generate_auth_token()
                    return {'token': token.decode('ascii')}, 200
                else:
                    return {'message': 'Password is incorrect'}, 404

        return {'message': 'User not found'}, 404

    def delete(self,id):
        return {'message': "Not developed yet"}, 404

    def put(self,id):
        return {'message': "Not developed yet"}, 404


@app.route('/')
def render_vue_events():
    return render_template("index.html")

@app.route('/userlogin')
def render_vue_login():
    return render_template("index.html")


api.add_resource(Artist, '/artist/<int:id>', '/artist')
api.add_resource(ArtistList, '/artists')

api.add_resource(Event, '/event/<int:id>', '/event')
api.add_resource(EventList, '/events')

api.add_resource(EventArtistsList, '/event/<int:id>/artists')
api.add_resource(EventArtist, '/event/<int:id_event>/artist/<int:id_artist>', '/event/<int:id_event>/artist')

api.add_resource(ArtistEventsList, '/artist/<int:id>/events')

api.add_resource(Orders, '/orders/<string:username>')
api.add_resource(OrdersList, '/orders')

api.add_resource(Accounts, '/account/<string:username>', '/account')
api.add_resource(AccountsList, '/accounts')

api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=False)
