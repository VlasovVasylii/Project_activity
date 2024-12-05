from flask import render_template, redirect, request, jsonify, flash, url_for
from flask_login import current_user, login_required
from app.extensions import db
from app.routes import main
from app.forms import CommentForm, MovieForm
from app.models import Comment, Movie, Show, Episode, Rating
from app.utils import get_recommended_movies, get_recommended_shows, save_video, get_video_path


@main.route('/')
def index():
    top_movies = Movie.query.order_by(Movie.external_rating.desc()).limit(10).all()
    top_shows = Show.query.order_by(Show.external_rating.desc()).limit(10).all()

    if current_user.is_authenticated:
        user_movies = get_recommended_movies(current_user.id)
        user_shows = get_recommended_shows(current_user.id)
    else:
        user_movies = top_movies
        user_shows = top_shows

    return render_template(
        'index.html', top_movies=user_movies, top_shows=user_shows
    )


@main.route('/list', methods=['GET'])
def content_list():
    content_type = request.args.get('type', 'movie')  # movie или show
    query = request.args.get('query', '').strip()

    if content_type == 'movie':
        content = Movie.query.filter(Movie.title.ilike(f"%{query}%")).all() if query else Movie.query.all()
    elif content_type == 'show':
        content = Show.query.filter(Show.title.ilike(f"%{query}%")).all() if query else Show.query.all()
    else:
        content = []

    return render_template('list.html', content=content, content_type=content_type)


@main.route("/watch/<content_type>/<int:content_id>", methods=["GET", "POST"])
def watch(content_type, content_id):
    form = CommentForm()
    content = None
    comments = None
    seasons = None
    selected_episode = None

    if content_type == "movie":
        content = Movie.query.get_or_404(content_id)
        comments = Comment.query.filter_by(movie_id=content_id).all()
    elif content_type == "show":
        content = Show.query.get_or_404(content_id)
        comments = Comment.query.filter_by(show_id=content_id).all()
        seasons = content.seasons

        # Выбор серии
        season_id = request.args.get("season", type=int)
        episode_id = request.args.get("episode", type=int)
        if season_id and episode_id:
            selected_episode = Episode.query.filter_by(season_id=season_id, id=episode_id).first()
        elif seasons:
            selected_episode = seasons[0].episodes[0] if seasons[0].episodes else None

    # Обработка формы комментариев
    if current_user.is_authenticated and form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            movie_id=content.id if content_type == "movie" else None,
            show_id=content.id if content_type == "show" else None
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(request.url)

    video_path = get_video_path(content_type, content.title, content.season_number if content_type == 'show' else None)
    return render_template(
        "watch.html",
        content=content,
        form=form,
        comments=comments,
        seasons=seasons,
        selected_episode=selected_episode,
        video_path=video_path
    )


@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    search_type = request.args.get('type', 'movie').strip()

    if search_type == 'movie':
        results = Movie.query.filter(Movie.title.ilike(f"%{query}%")).all()
    elif search_type == 'show':
        results = Show.query.filter(Show.title.ilike(f"%{query}%")).all()
    else:
        results = []

    return render_template('search_results.html', results=results, search_type=search_type)


@main.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    content_type = request.args.get('type', 'movie')
    if content_type == 'movie':
        recommendations = get_recommended_movies(current_user.id)
    elif content_type == 'show':
        recommendations = get_recommended_shows(current_user.id)
    else:
        recommendations = []

    return render_template('recommendations.html', recommendations=recommendations, content_type=content_type)


@main.route('/rate/<content_type>/<int:content_id>', methods=['POST'])
@login_required
def rate_content(content_type, content_id):
    try:
        rating_value = int(request.json.get('rating', 0))
        if not (1 <= rating_value <= 10):
            raise ValueError("Invalid rating")
    except ValueError:
        return jsonify({'error': 'Rating must be between 1 and 10'}), 400

    content = None
    if content_type == 'movie':
        content = Movie.query.get_or_404(content_id)
    elif content_type == 'show':
        content = Show.query.get_or_404(content_id)

    if not content:
        return jsonify({'error': 'Content not found'}), 404

    rating = Rating.query.filter_by(user_id=current_user.id, **{f"{content_type}_id": content_id}).first()
    if rating:
        rating.rating = rating_value
    else:
        rating = Rating(user_id=current_user.id, **{f"{content_type}_id": content_id}, rating=rating_value)
        db.session.add(rating)
    db.session.commit()

    return jsonify({'message': 'Rating submitted', 'average_rating': content.average_rating}), 200


@main.route('/add/<content_type>', methods=['GET', 'POST'])
@login_required
def add_content(content_type):
    form = MovieForm()
    if form.validate_on_submit():
        video_file = form.video.data
        thumbnail_file = form.thumbnail.data

        if content_type == 'movie':
            video_path = save_video(video_file, content_type)
            thumbnail_path = save_video(thumbnail_file, 'movie')  # Сохраняем изображение
            content = Movie(
                title=form.title.data,
                description=form.description.data,
                video_url=video_path,
                thumbnail_url=thumbnail_path,
                genre=form.genre.data,
                year=form.year.data
            )
        elif content_type == 'show':
            season_number = request.form.get('season_number', type=int)
            video_path = save_video(video_file, content_type, season=season_number)
            thumbnail_path = save_video(thumbnail_file, 'show')  # Сохраняем изображение
            content = Show(
                title=form.title.data,
                description=form.description.data,
                genre=form.genre.data,
                year=form.year.data,
                thumbnail_url=thumbnail_path
            )
        else:
            flash('Invalid content type.', 'danger')
            return redirect(url_for('main.index'))

        db.session.add(content)
        db.session.commit()
        flash(f'{content_type.capitalize()} added successfully.', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_content.html', form=form, content_type=content_type)


@main.route('/search', methods=['GET'])
def advanced_search():
    content_type = request.args.get('type', 'movie')
    genre = request.args.get('genre')
    min_rating = request.args.get('min_rating', type=float)
    max_rating = request.args.get('max_rating', type=float)
    year = request.args.get('year', type=int)

    query = Movie.query if content_type == 'movie' else Show.query

    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if min_rating:
        query = query.filter(Movie.average_rating >= min_rating)
    if max_rating:
        query = query.filter(Movie.average_rating <= max_rating)
    if year:
        query = query.filter(Movie.year == year)

    results = query.all()
    return render_template('search_results.html', results=results, content_type=content_type)


@main.route('/comments/<content_type>/<int:content_id>', methods=['GET'])
def get_comments(content_type, content_id):
    sort_by = request.args.get('sort_by', 'new')
    comments = None

    if content_type == 'movie':
        comments = Comment.query.filter_by(movie_id=content_id)
    elif content_type == 'show':
        comments = Comment.query.filter_by(show_id=content_id)

    if sort_by == 'popular':
        comments = comments.order_by(Comment.likes.desc())
    else:
        comments = comments.order_by(Comment.timestamp.desc())

    comments = comments.all()
    return render_template('comments.html', comments=comments, content_type=content_type)
