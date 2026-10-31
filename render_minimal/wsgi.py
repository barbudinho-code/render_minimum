from flask import Flask

application = Flask(__name__)


@application.route("/")
def hello():
    return "Hello, World!"


@application.route("/about")
def about():
    return "<h1>About Page</h1><p>This is the about page.</p>"


if __name__ == "__main__":
    application.run(debug=True)
