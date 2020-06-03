from db import db

artists = db.Table('event_artists', db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
                   db.Column('artist_id', db.Integer, db.ForeignKey('artists.id')))

class EventModel(db.Model):
    __tablename__ = 'events' #This is table name
    __tableargs__ = (db.UniqueConstraint('name', 'date', 'city'))

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    place = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    total_available_tickets = db.Column(db.Integer, nullable=False)
    artists = db.relationship('ArtistModel', secondary=artists, backref=db.backref('events', lazy='dynamic'))

    def __init__(self, name, place, city, date, price, total_available_tickets):
        self.name = name
        self.place = place
        self.city = city
        self.date = date
        self.price = price
        self.total_available_tickets = total_available_tickets

    def json(self):
        artistList = []
        for artist in self.artists:
            artistList.append(artist)

        return {
            "id": self.id,
            "name": self.name,
            "place": self.place,
            "city": self.city,
            "date": self.date,
            "artists": [artist.json() for artist in artistList],
            "price": self.price,
            "total_available_tickets": self.total_available_tickets
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
