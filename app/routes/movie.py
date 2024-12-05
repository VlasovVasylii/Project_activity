from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.routes import movie
from app.forms import MovieForm
from app.models import Movie, Rating, Comment
from app.utils import upload_to_s3, get_recommended_movies


@movie.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        thumbnail_url = upload_to_s3(form.thumbnail.data, 'thumbnails')
        video_url = upload_to_s3(form.video.data, 'videos')
        new_movie = Movie(
            title=form.title.data,
            description=form.description.data,
            thumbnail_url=thumbnail_url,
            video_url=video_url,
            genre=form.genre.data,
            year=form.year.data
        )
        db.session.add(new_movie)
        db.session.commit()
        flash('Movie added successfully.', 'success')
        return redirect(url_for('movie.list_movies'))
    return render_template('movie/add.html', form=form)


@movie.route("/search", methods=["GET"])
def advanced_search():
    genre = request.args.get("genre")
    min_rating = request.args.get("min_rating", type=float)
    max_rating = request.args.get("max_rating", type=float)
    year = request.args.get("year", type=int)
    query = Movie.query
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if min_rating:
        query = query.filter(Movie.average_rating >= min_rating)
    if max_rating:
        query = query.filter(Movie.average_rating <= max_rating)
    if year:
        query = query.filter(Movie.year == year)
    movies = query.all()
    return render_template("movie/list.html", movies=movies)


@movie.route('/<int:movie_id>/rate', methods=['POST'])
@login_required
def rate_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    try:
        rating_value = int(request.json.get('rating', 0))
        if not (1 <= rating_value <= 10):
            raise ValueError("Invalid rating")
    except ValueError:
        return jsonify({'error': 'Rating must be between 1 and 10'}), 400

    rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if rating:
        rating.rating = rating_value
    else:
        rating = Rating(user_id=current_user.id, movie_id=movie_id, rating=rating_value)
        db.session.add(rating)
    db.session.commit()

    return jsonify({'message': 'Rating submitted', 'average_rating': movie.average_rating}), 200


@movie.route('/<int:movie_id>/comments', methods=['GET'])
def get_comments(movie_id):
    sort_by = request.args.get('sort_by', 'new')
    if sort_by == 'popular':
        comments = Comment.query.filter_by(movie_id=movie_id).order_by(Comment.likes.desc()).all()
    else:
        comments = Comment.query.filter_by(movie_id=movie_id).order_by(Comment.timestamp.desc()).all()
    return comments

