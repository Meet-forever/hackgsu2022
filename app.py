from flask import Flask, render_template, request, session, url_for, redirect, abort, Response
import json
import requests
import dotenv
from datetime import timedelta
import pandas as pd
import numpy as np
env = dotenv.dotenv_values()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'notasecretkey'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
website_link = "https://simply-get-that-job.herokuapp.com" 
# website_link = "http://localhost:5000"

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        account_error = False
        missing = False
        if email and password:
            if email == 'guest@hack.com' and password == 'guest':
                session['email'] = email
                session['name'] = 'guest' 
                session.permanent = True
                return redirect('/accounts/guest')
            else:
                account_error = True
                return render_template('login.html', account_error=account_error)
        else:
            missing = True
            return render_template('login.html', missing=missing)
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        account_error = False
        missing = False
        if email and password:
            if email == 'guest@hack.com' and password == 'guest':
                return redirect('/login')
            else:
                account_error = True
                return render_template('register.html', account_error=account_error)
        else:
            missing = True
            return render_template('register.html', missing=missing)

    return render_template('register.html')



@app.route('/accounts/<user>', methods=['GET', 'POST'])
def get_account(user):

    if user not in session['name']:
        return redirect('/login')
    else:
        email = session['email']
        return render_template('user_account.html', user=user, email = email, website_link=website_link)


@app.route('/accounts/data/<user>', methods=['POST'])
def get_data(user):
    if user not in session['name']:
        return redirect('/login')
    try:
        URL = "https://remoteok.com/api"
        keys = ['date', 'company', 'position', 'tags', 'location', 'url']
        positions = request.form['skills']
        positions = positions.strip().split(',')
        print(positions)
        for i, ps in enumerate(positions):
            positions[i] = ps.strip().lower()

        def get_job():
            resp = requests.get(URL)
            results = resp.json()

            jobs = []
            for result in results:
                job = {k: v for k, v in result.items() if k in keys}
                if job:
                    tags = job.get('tags')
                    pos = job.get('position')
                    pos = {po.lower for po in pos}
                    tags = {tag.lower() for tag in tags}
                    if pos.intersection(positions):
                        jobs.append(job)
                    if tags.intersection(positions):
                        jobs.append(job)
            return jobs
        
        search_job = get_job()
        df = pd.DataFrame(search_job)
        return Response(
            df.to_csv(),
            mimetype="text/csv",
            headers={"Content-disposition":
            "attachment; filename=data.csv"})
    except FileNotFoundError:
        abort(404)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)


