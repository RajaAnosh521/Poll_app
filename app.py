import os
import pandas as pd
from flask import Flask, render_template, redirect, request, url_for, make_response

app = Flask(__name__)

# Check if the CSV file exists, if not create it with the correct structure
if not os.path.exists("polls.csv"):
    structure = {
        "id": [],
        "poll": [],
        "option1": [],
        "option2": [],
        "option3": [],
        "vote1": [],
        "vote2": [],
        "vote3": [],
    }
    pd.DataFrame(structure).set_index("id").to_csv("polls.csv")

polls_df = pd.read_csv("polls.csv").set_index("id")

@app.route("/")
def index():
    polls = polls_df.to_dict(orient='index')  # Convert DataFrame to dictionary
    return render_template("index.html", polls=polls)

@app.route("/polls/<id>")
def poll(id):
    try:
        poll = polls_df.loc[int(id)]
        return render_template("show_poll.html", poll=poll)
    except KeyError:
        return "Poll not found", 404

@app.route("/polls", methods=["GET", "POST"])
def create_poll():
    if request.method == "GET":
        return render_template("new_poll.html")
    elif request.method == "POST":
        poll = request.form['poll']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        new_id = max(polls_df.index.values) + 1 if not polls_df.empty else 0
        polls_df.loc[new_id] = [poll, option1, option2, option3, 0, 0, 0]
        polls_df.to_csv("polls.csv")
        return redirect(url_for('index'))

@app.route("/vote/<id>/<option>")
def vote(id, option):
    if request.cookies.get(f"votes_{id}_cookie") is None:
        polls_df.at[int(id), "vote"+str(option)] += 1
        polls_df.to_csv("polls.csv")
        response = make_response(redirect(url_for("poll", id=id)))
        response.set_cookie(f"Vote_{id}_cookie", str(option)) 
        return response
    else:
        return "Cannot vote more than once!"

if __name__ == "__main__":
    app.run(host="localhost", debug=True)
