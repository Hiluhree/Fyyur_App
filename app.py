#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
from itertools import count
import json
import sys
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, jsonify, redirect, url_for
from flask_moment import Moment
from markupsafe import Markup
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:eldoret@localhost:5432/fyyur_db'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #venues = Venue.query.order_by(Venue.state, Venue.city).all()
  data = []
  VenueLocationQuery = Venue.query.distinct(Venue.state, Venue.city).all() #Getting unique citiess

  VenueLocations = {}
  for VenueLocation in VenueLocationQuery:
    VenueLocations = {
      'city': VenueLocation.city,
      'state': VenueLocation.state,
      'venues': []
    }

    venues = Venue.query.filter_by(state=VenueLocation.state, city=VenueLocation.city).all()
    for venue in venues:
      VenueLocations['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': Show.query.join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).count()
      })
      data.append(VenueLocations)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  VenueSearch = '%{}%'.format(search_term)
  response = {
    'count': Venue.query.filter(Venue.name.ilike(VenueSearch)).count(),
    'data': []
  }
  VenueSearchResults = Venue.query.filter(Venue.name.ilike(VenueSearch)).all()

  for result in VenueSearchResults:
    response['data'].append({
      'id': result.id,
      'name': result.name,
      'now_upcoming_shows': Show.query.join(Venue).filter(Show.venue_id==result.id).filter(Show.start_time > datetime.now()).count()
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  PastShowsQuery = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(datetime.today()>Show.start_time).all()
  PastShows = []
  for show in PastShowsQuery:
    PastShows.append({
      'artist_id': show.artist_id,
      'artist_name': Artist.query.get(show.artist_id).name,
      'artist_image_link': Artist.query.get(show.artist_id).image_link,
      'start_time': show.start_time
    })

  UpcomingShowsQuery = Show.query.join(Venue).filter(Show.venue_id==venue_id).filter(datetime.today()>Show.start_time).all()
  UpcomingShows = []
  for show in UpcomingShowsQuery:
    UpcomingShows.append({
      'artist_id': show.artist_id,
      'artist_name': Artist.query.get(show.artist_id).name,
      'artist_image_link': Artist.query.get(show.artist_id).image_link,
      'start_time': show.start_time
    })

  PastShowsCount = len(PastShows)
  UpcomingShowsCount = len(UpcomingShows)

  VenueInfo = Venue.query.get(venue_id)

  data = {
    'id': VenueInfo.id,
    'name': VenueInfo.name,
    'genres': VenueInfo.genres,
    'address': VenueInfo.address,
    'city': VenueInfo.city,
    'state': VenueInfo.state,
    'phone': VenueInfo.phone,
    'website_link': VenueInfo.website_link,
    'facebook_link': VenueInfo.facebook_link,
    'seeking_talent': VenueInfo.seeking_talent,
    'seeking_description': VenueInfo.seeking_description,
    'image_link': VenueInfo.image_link,
    'PastShows': PastShows,
    'UpcomingShows': UpcomingShows,
    'PastShowsCount': PastShowsCount,
    'UpcomingShows': UpcomingShowsCount
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  error = False
  # DONE: modify data to be the data object returned from db insertion
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)
    venue.website_link = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    if error:
      flash('An error occured. Venue ' + request.form['name'] + ' Could not be listed')
    else:
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    DeleteVenue = Venue.query.get(venue_id)
    db.session.delete(DeleteVenue)
    db.session.commit()
    flash(f'<Venue {venue_id} successfully deleted')

  except:
    db.session.rollback()
    flash(f'Error. Venue {venue_id} not deleted!')

  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # DONE: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  error = False
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)
    venue.facebook_link = request.form['facebook_link']
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Venue ' + request.form['name'] + ' could be update.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  ARTISTS
#  ----------------------------------------------------------------

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  form = ArtistForm(request.form)
  error = False
  # DONE: modify data to be the data object returned from db insertion
  if form.validate_on_submit():
    data = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = ','.join(form.genres.data),
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data)

    try:
      db.session.add(data)
      db.session.commit()

      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      
    except:
      error = True
      db.session.rollback()
      
    finally:
      db.session.close()
  
  else:
    # DONE: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    for field, message in form.errors.items():
      flash(f'The ({message}). Kindly check the following field: {field}.')
    
  return render_template('pages/home.html')

# Get Artists

@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data = []
  artist_query = Artist.query.all()

  for artist in artist_query:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  ArtistSearch = '%{}%'.format(search_term)
  response = {
    'count': Artist.query.filter(Artist.name.ilike(ArtistSearch)).count(),
    'data': []
  }
  ArtistSearchResults = Artist.query.filter(Artist.name.ilike(ArtistSearch)).all()

  for result in ArtistSearchResults:
    response['data'].append({
      'id': result.id,
      'name': result.name,
      'now_upcoming_shows': Show.query.join(Artist).filter(Show.artist_id==result.id).filter(Show.start_time > datetime.now()).count()
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  # DONE: replace with real artist data from the artist table, using artist_id
  PastShowsQuery = Show.query.join(Artist).filter(Show.Artist_id==artist_id).filter(datetime.today()>Show.start_time).all()
  PastShows = []
  for show in PastShowsQuery:
    PastShows.append({
      'artist_id': show.artist_id,
      'artist_name': Artist.query.get(show.artist_id).name,
      'artist_image_link': Artist.query.get(show.artist_id).image_link,
      'start_time': show.start_time
    })

  UpcomingShowsQuery = Show.query.join(Artist).filter(Show.artist_id==artist_id).filter(datetime.today()>Show.start_time).all()
  UpcomingShows = []
  for show in UpcomingShowsQuery:
    UpcomingShows.append({
      'artist_id': show.artist_id,
      'artist_name': Artist.query.get(show.artist_id).name,
      'artist_image_link': Artist.query.get(show.artist_id).image_link,
      'start_time': show.start_time
    })

  PastShowsCount = len(PastShows)
  UpcomingShowsCount = len(UpcomingShows)

  ArtistInfo = Artist.query.get(artist_id)

  data = {
    'id': ArtistInfo.id,
    'name': ArtistInfo.name,
    'genres': ArtistInfo.genres,
    'address': ArtistInfo.address,
    'city': ArtistInfo.city,
    'state': ArtistInfo.state,
    'phone': ArtistInfo.phone,
    'website_link': ArtistInfo.website_link,
    'facebook_link': ArtistInfo.facebook_link,
    'seeking_venue': ArtistInfo.seeking_venue,
    'seeking_description': ArtistInfo.seeking_description,
    'image_link': ArtistInfo.image_link,
    'PastShows': PastShows,
    'UpcomingShows': UpcomingShows,
    'PastShowsCount': PastShowsCount,
    'UpcomingShows': UpcomingShowsCount
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update Artists
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  # DONE: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  Form = ArtistForm(request.form)
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    tmp_genres = request.form.getlist['genres']
    artist.genres = ','.join(tmp_genres)
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_artist = request.form['seeking_venue']
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Artist ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  return redirect(url_for(show_artist), artist_id=artist_id)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data=[]
  for show in shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': Venue.query.get(show.venue_id).name,
      'artist_id': show.artist.id,
      'artist_name': Artist.query.get(show.artist_id).name,
      'artist_image_link': Artist.query.get(show.artist_id).image_link,
      'start_time': show.start_time.isoformat()
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    data = Show(
      venue_id = form.venue_id.data,
      artist_id = form.artist_id.data,
      start_time = str(form.start_time.data))
    try:
        db.session.add(data)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Requested show could not be listed.')
        else:
            flash('Requested show was successfully listed')
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''