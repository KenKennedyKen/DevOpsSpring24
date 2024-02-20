import os
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

basedir = Path(__file__).resolve().parent

#supposedly helps SQL handle data better
app = Flask(__name__)

# configuration
app.config['DATABASE'] = "flaskr.db"
app.config['SECRET_KEY'] = "change_me"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", f"sqlite:///{Path(basedir).joinpath(app.config['DATABASE'])}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')  # Upload folder configuration
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed extensions

db = SQLAlchemy(app)

#makes directory for storing images
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# load the config - commenting out because might not be needed
#app.config.from_object(__name__)

from project import models
from project.models import User

with app.app_context():
    db.create_all()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify({"status": 0, "message": "Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Post)
    return render_template("index.html", entries=entries)


@app.route("/add", methods=["POST"])
def add_entry():
    """Adds new post to the database."""
    if not session.get("logged_in"):
        abort(401)
    title = request.form["title"]
    text = request.form["text"]
    image = request.files.get("image")  # Get the uploaded image file

    image_filename = None
    if image and allowed_file(image.filename):  # Make sure the file is allowed
        image_filename = secure_filename(image.filename)  # Secure the filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)  # Save the file to the UPLOAD_FOLDER

    # Create a new Post instance with the image filename
    new_entry = models.Post(title=title, text=text, image_filename=image_filename)
    db.session.add(new_entry)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))

def allowed_file(filename):
    """Check if the file's extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

#here is a new login route attempt
@app.route("/login", methods=["GET", "POST"])
def login():
    #User login/authentication/session management
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            error = "Invalid username or password"
        else:
            session["logged_in"] = True
            flash("You were logged in logged in logged in in in")
            return redirect(url_for("index"))
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    """User logout/authentication/session management."""
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("index"))


@app.route("/delete/<int:post_id>", methods=["GET"])
@login_required
def delete_entry(post_id):
    """Deletes post from database."""
    result = {"status": 0, "message": "Error"}
    try:
        new_id = post_id
        db.session.query(models.Post).filter_by(id=new_id).delete()
        db.session.commit()
        result = {"status": 1, "message": "Post Deleted"}
        flash("The entry was deleted.")
    except Exception as e:
        result = {"status": 0, "message": repr(e)}
    return jsonify(result)


@app.route("/search/", methods=["GET"])
def search():
    query = request.args.get("query")
    entries = db.session.query(models.Post)
    if query:
        return render_template("search.html", entries=entries, query=query)
    return render_template("search.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))
        # Create new user instance
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        flash("User successfully registered")
        return redirect(url_for("login"))
    return render_template("register.html")


if __name__ == "__main__":
    app.run()
#change this to make it run from here?