from flask import render_template, redirect, request
from flask_login import current_user, login_required
from app.extensions import db
from app.routes import main
from app.forms import CommentForm
from app.models import Comment, Movie, Show, Episode
from app.utils import get_recommended_movies, get_recommended_shows


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

    return render_template(
        "watch.html",
        content=content,
        form=form,
        comments=comments,
        seasons=seasons,
        selected_episode=selected_episode
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
