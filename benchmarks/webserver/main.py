import time

from flask import Flask, request, render_template
import timeit
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


@app.route('/')
def index():
    start = time.time()
    for i in range(10000):
        test()
    duration = time.time() - start
    return render_template('index.html', time=duration)


def test():
    lst = []
    for i in range(100):
        lst.append(i)


def create_app():
    return app


if __name__ == "__main__":
    create_app()
