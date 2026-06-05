import functools
import os
import random

from config import config_map
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_wtf.csrf import generate_csrf
from models import City, SearchHistory, User, db
from test_api import get_weather, format_weather, get_forecast
from forms import LoginForm, RegisterForm, SearchForm

app = Flask(__name__)
env = os.environ.get("FLASK_ENV", "development")
app.config.from_object(config_map.get(env, config_map["development"]))

db.init_app(app)


WEATHER_TYPE_RULES = [
    (("temporale",), "storm"),
    (("pioggia", "rovesci"), "rain"),
    (("neve",), "snow"),
    (("nuvol", "coperto"), "cloudy"),
    (("nebbia", "foschia"), "fog"),
    (("sereno",), "clear"),
]

PARTICLE_CONFIG = {
    "rain":         {"emoji": "💧",  "count": 40, "duration": (0.7, 1.4)},
    "storm":        {"emoji": "💧",  "count": 40, "duration": (0.7, 1.4)},
    "snow":         {"emoji": "❄️", "count": 30, "duration": (2.0, 4.0)},
    "cloudy":       {"emoji": "☁️", "count": 8,  "duration": (4.0, 7.0)},
    "cloudy_night": {"emoji": "☁️", "count": 8,  "duration": (4.0, 7.0)},
    "fog":          {"emoji": "🌫️", "count": 6,  "duration": (5.0, 8.0)},
    "clear":        {"emoji": "☀️", "count": 6,  "duration": (1.5, 2.5)},
    "clear_night":  {"emoji": "🌙", "count": 6,  "duration": (1.5, 2.5)},
}


def weather_type_from(description, is_night=False):
    desc = (description or "").lower()
    for keywords, wtype in WEATHER_TYPE_RULES:
        if any(k in desc for k in keywords):
            if is_night and wtype in ("clear", "cloudy"):
                return wtype + "_night"
            return wtype
    return "clear_night" if is_night else "clear"


def generate_particles(weather_type):
    cfg = PARTICLE_CONFIG.get(weather_type, PARTICLE_CONFIG["clear"])
    return [
        {
            "left": round(random.uniform(0, 100), 2),
            "top": round(random.uniform(5, 60), 2),
            "delay": round(random.uniform(0, 1.5), 2),
            "duration": round(random.uniform(*cfg["duration"]), 2),
            "emoji": cfg["emoji"],
        }
        for _ in range(cfg["count"])
    ]


CITY_IMAGES = {
    "Rome,IT": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1920&q=80",
    "Tokyo,JP": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1920&q=80",
    "Rio de Janeiro,BR": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=1920&q=80",
    "Sydney,AU": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=1920&q=80",
    "Reykjavik,IS": "https://images.unsplash.com/photo-1504284769763-81b22fcdb831?auto=format&fit=crop&w=1920&q=80",
}
DEFAULT_CITY_IMAGE = "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=1920&q=80"


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Devi effettuare il login", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return User.query.get(user_id)


@app.context_processor
def inject_current_user():
    return {"current_user": get_current_user(), "csrf_token": generate_csrf}


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])

    city = "Rome,It"
    weather = format_weather(get_weather(city))
    if weather is None:
        flash("Impossibile caricare i dati meteo. Controlla la chiave API nel file .env.", "error")
        weather = {"city": "Roma", "description": "clear sky", "temperature": "--", "humidity": "--", "is_night": False}
    forecast = get_forecast(city)
    bg_image = CITY_IMAGES.get(city, DEFAULT_CITY_IMAGE)
    weather_type = weather_type_from(weather["description"], weather.get("is_night", False))
    particles = generate_particles(weather_type)

    cities_weather = []
    for saved_city in user.cities:
        raw = get_weather(saved_city.name)
        if raw is None:
            continue
        cities_weather.append({
            "city_id": saved_city.id,
            "city_name": raw.get("name", saved_city.name),
            "temp": int(raw["main"]["temp"]),
            "description": raw["weather"][0]["description"],
            "humidity": raw["main"]["humidity"],
            "country": raw.get("sys", {}).get("country", saved_city.country or ""),
        })

    return render_template(
        "dashboard.html",
        weather=weather,
        forecast=forecast,
        bg_image=bg_image,
        weather_type=weather_type,
        particles=particles,
        user=user,
        cities_weather=cities_weather,
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    weather_data = None
    searched_city = None

    if form.validate_on_submit():
        searched_city = form.city.data
        weather_info = get_weather(searched_city)

        if weather_info:
            weather_data = format_weather(weather_info)
            if "user_id" in session:
                try:
                    search_entry = SearchHistory(city_name=searched_city, user_id=session["user_id"])
                    db.session.add(search_entry)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
        else:
            flash("Città non trovata", "error")

    return render_template("search.html", form=form, weather_data=weather_data, searched_city=searched_city)


@app.route("/delete_city/<int:city_id>", methods=["POST"])
@login_required
def delete_city(city_id):
    user = User.query.get(session["user_id"])
    city = City.query.filter_by(id=city_id, user_id=user.id).first()

    if not city:
        flash("Città non trovata.", "error")
        return redirect(url_for("dashboard"))

    db.session.delete(city)
    try:
        db.session.commit()
        flash(f"'{city.name}' rimossa dalla lista.", "success")
    except Exception:
        db.session.rollback()
        flash("Errore durante la rimozione. Riprova.", "error")

    return redirect(url_for("dashboard"))


@app.route("/save_city", methods=["POST"])
@login_required
def save_city():
    city_name = request.form.get("city_name", "").strip()
    country = request.form.get("country", "").strip()
    lat = request.form.get("lat", type=float)
    lon = request.form.get("lon", type=float)

    user = User.query.get(session["user_id"])

    MAX_CITIES = 6

    if City.query.filter_by(user_id=user.id, name=city_name).first():
        flash("Città già salvata", "warning")
        return redirect(url_for("dashboard"))

    if City.query.filter_by(user_id=user.id).count() >= MAX_CITIES:
        flash("Hai raggiunto il limite di 6 città salvate. Rimuovi una città per aggiungerne un'altra.", "warning")
        return redirect(url_for("dashboard"))

    city = City(name=city_name, country=country, lat=lat, lon=lon, user_id=user.id)
    db.session.add(city)
    try:
        db.session.commit()
        flash("Città salvata con successo!", "success")
    except Exception:
        db.session.rollback()
        flash("Errore durante il salvataggio. Riprova.", "error")

    return redirect(url_for("dashboard"))


@app.route("/history")
@login_required
def history():
    searches = (
        SearchHistory.query
        .filter_by(user_id=session["user_id"])
        .order_by(SearchHistory.searched_at.desc())
        .limit(10)
        .all()
    )
    total_searches = SearchHistory.query.filter_by(user_id=session["user_id"]).count()
    return render_template("history.html", searches=searches, total_searches=total_searches)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Username o password errati", "error")
            return render_template("login.html", form=form)

        session["user_id"] = user.id
        flash("Login effettuato!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout effettuato", "info")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash("Username già in uso.", "error")
            return render_template("register.html", form=form)

        if User.query.filter_by(email=email).first():
            flash("Email già registrata.", "error")
            return render_template("register.html", form=form)

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Errore durante la creazione dell'account. Riprova.", "error")
            return render_template("register.html", form=form)

        flash("Account creato! Ora puoi fare login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


# ---------------------------------------------------------------------------
# Private routes (require authentication)
# ---------------------------------------------------------------------------

@app.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user_id"])
    cities_count = len(user.cities)
    searches_count = SearchHistory.query.filter_by(user_id=user.id).count()
    most_searched = (
        db.session.query(SearchHistory.city_name, db.func.count(SearchHistory.city_name).label("cnt"))
        .filter_by(user_id=user.id)
        .group_by(SearchHistory.city_name)
        .order_by(db.text("cnt DESC"))
        .first()
    )
    most_searched_city = most_searched.city_name if most_searched else None
    return render_template(
        "profile.html",
        user=user,
        cities_count=cities_count,
        searches_count=searches_count,
        most_searched_city=most_searched_city,
    )


# ---------------------------------------------------------------------------
# Legacy / demo routes
# ---------------------------------------------------------------------------

@app.route("/roma")
def roma():
    data = get_weather("Rome,It")
    weather = format_weather(data)
    return render_template("meteo.html", weather=weather)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
