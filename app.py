from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
from textblob import TextBlob
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Create the SQLite database if it doesn't exist
def create_database():
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mood_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        mood TEXT,
        journal_entry TEXT,
        sentiment_score REAL
    )''')
    conn.commit()
    conn.close()

create_database()

# Sentiment analysis function
def analyze_sentiment(journal_entry):
    blob = TextBlob(journal_entry)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

# Home page to submit mood and journal
@app.route('/')
def home():
    return render_template('index.html')

# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        mood = request.form['mood']
        journal_entry = request.form['journal_entry']
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sentiment_score = analyze_sentiment(journal_entry)

        conn = sqlite3.connect('mood_tracker.db')
        c = conn.cursor()
        c.execute("INSERT INTO mood_data (date, mood, journal_entry, sentiment_score) VALUES (?, ?, ?, ?)",
                  (date, mood, journal_entry, sentiment_score))
        conn.commit()
        conn.close()

        return redirect('/history')

# History page to see all entries
@app.route('/history')
def history():
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    c.execute("SELECT * FROM mood_data ORDER BY date DESC")
    entries = c.fetchall()
    conn.close()

    moods = [entry[2] for entry in entries]
    dates = [entry[1] for entry in entries]
    sentiment_scores = [entry[4] for entry in entries]

    plot_url = plot_sentiment(sentiment_scores, dates)
    return render_template('history.html', entries=entries, dates=dates, sentiment_scores=sentiment_scores, moods=moods, plot_url=plot_url)

# Plot the sentiment scores
def plot_sentiment(sentiment_scores, dates):
    plt.figure(figsize=(10,5))
    plt.plot(dates, sentiment_scores, marker='o')
    plt.title('Sentiment Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url

if __name__ == "__main__":
    app.run(debug=True)
