from flask import render_template, request
from app.models import Show
from app.routes import show


@show.route("/search", methods=["GET"])
def advanced_search():
    genre = request.args.get("genre")
    min_rating = request.args.get("min_rating", type=float)
    max_rating = request.args.get("max_rating", type=float)
    year = request.args.get("year", type=int)
    query = Show.query
    if genre:
        query = query.filter(Show.genre.ilike(f"%{genre}%"))
    if min_rating:
        query = query.filter(Show.average_rating >= min_rating)
    if max_rating:
        query = query.filter(Show.average_rating <= max_rating)
    if year:
        query = query.filter(Show.year == year)
    shows = query.all()
    return render_template('show/list.html', shows=shows)
