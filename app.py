from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/about')
def about():
    return '<h1>About Page</h1><p>This is the about page.</p>'


if __name__ == '__main__':
    app.run(debug=True)
