from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models. For Venues, Artists and Shows
#----------------------------------------------------------------------------#
""" Venues Model """
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))

    artists = db.relationship('Artist', secondary='shows')
    shows = db.relationship('Show', backref=('venues'))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def to_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres.split(','), # convert string to list
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website_link': self.website_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description
      }

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

""" Artist Model """
class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False) #Added Looking for Venues Field
    seeking_description = db.Column(db.String(120)) #Adding seeking description field

    venues = db.relationship('Venue', secondary='shows')
    shows = db.relationship('Show', backref=('artists'))

    def to_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres.split(','), # convert string to list
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website_link': self.website_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description
      }

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

""" Show Model """

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  venue = db.relationship('Venue')
  artist = db.relationship('Artist')

  def show_artist(self):
    return {
      'artist_id': self.artist_id,
      'artist_name': self.artist.name,
      'artist_image_link': self.artist.image_link,
      #code to convert datetime to string
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }

  def show_venue(self):
    return {
      'venue_id': self.venue_id,
      'venue_name': self.venue.name,
      'venue_image_link': self.venue.image_link,
      #code to convert datetime to string
      'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
  

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.