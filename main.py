from livereload import Server
from flask import Flask, Response, make_response, render_template, url_for, request, jsonify, redirect

import pandas as pd
import numpy as np

import os 
import re
import base64

template_folder = "templates/"
static_folder = "static/"
csv_file = "csv/laptop_kaggle.csv"

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, static_url_path="/")

@app.route('/')
def home():
    return render_template('index.html')



if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch(template_folder)
    server.watch(static_folder)
    server.serve(debug=True, host='0.0.0.0', port=5000)
