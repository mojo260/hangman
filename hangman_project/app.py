# Importing the os module for file path operations
import os

# Importing necessary Flask components for web app functionality
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Importing random module to select random words for the game
import random

# Creating an instance of the Flask application
app = Flask(__name__)

# Setting a secret key to enable session management securely
app.secret_key = 'hangman-secret'


# Function to load words from a file, categorized by category and difficulty
def load_words(filepath):
    words = {}  # Dictionary to store words grouped by category and difficulty
    with open(filepath, 'r') as f:  # Open the words file
        for line in f:
            line = line.strip()  # Remove leading/trailing whitespace
            if not line or line.startswith('#'):  # Skip empty lines or comments
                continue
            try:
                category, difficulty, word = line.split(':')  # Extract category, difficulty, and word
            except ValueError:
                continue  # Skip malformed lines
            # Organize words in a nested dictionary structure
            words.setdefault(category, {}).setdefault(difficulty, []).append(word)
    return words


# Load the words into the WORDS dictionary from 'words.txt' in the same directory
WORDS = load_words(os.path.join(os.path.dirname(__file__), 'words.txt'))


# Function to start a new game by initializing the session state
def start_game(category, difficulty):
    # Randomly pick a word based on selected category and difficulty
    word = random.choice(WORDS[category][difficulty])
    session['word'] = word  # Store the selected word in session
    session['guesses'] = []  # Initialize an empty list of guessed letters
    session['lives'] = 6  # Set initial number of lives
    session['category'] = category  # Store the chosen category
    session['difficulty'] = difficulty  # Store the chosen difficulty


# Route to render the home page
@app.route('/home')
def home():
    return render_template('home.html')


# Main route for the game
@app.route('/')
def index():
    # Get difficulty and category from request or session, default if missing
    difficulty = request.args.get('difficulty') or session.get('difficulty', 'easy')
    category = request.args.get('category') or session.get('category', 'fruits')

    # Start a new game if one hasn't been started or if difficulty/category changed
    if ('word' not in session or
            session.get('difficulty') != difficulty or
            session.get('category') != category):
        start_game(category, difficulty)

    # Render the main game page with selected settings
    return render_template('index.html', difficulty=difficulty, category=category)


# Route to handle guessing a letter
@app.route('/guess', methods=['POST'])
def guess():
    # Get the guessed letter from the form input and convert to lowercase
    letter = request.form['letter'].lower()

    # Retrieve current game state from session
    word = session.get('word', '')
    guesses = session.get('guesses', [])
    lives = session.get('lives', 6)

    # Only process new guesses
    if letter and letter not in guesses:
        guesses.append(letter)  # Add new guess
        if letter not in word:
            lives -= 1  # Deduct a life if guess is incorrect

    # Update session with new guesses and lives
    session['guesses'] = guesses
    session['lives'] = lives

    # Create a display version of the word showing guessed letters and underscores
    display_word = ''.join([c if c in guesses else '_' for c in word])

    # Determine if the game is over (either win or lose)
    game_over = lives == 0 or '_' not in display_word

    # Count incorrect guesses to determine hangman stage
    wrong_guesses = len([g for g in guesses if g not in word])

    # Return JSON response with updated game state for the frontend
    return jsonify({
        'display_word': display_word,
        'guesses': guesses,
        'lives': lives,
        'game_over': game_over,
        'won': '_' not in display_word,
        'stage': min(wrong_guesses + 1, 7)  # Determines hangman drawing stage (up to 7)
    })
@app.route('/rules')
def rules():
    return render_template('rules.html')

# Route to reset the game and start a new one
@app.route('/reset', methods=['POST'])
def reset():
    # Get current category and difficulty from session, use defaults if missing
    category = session.get('category', 'fruits')
    difficulty = session.get('difficulty', 'easy')

    # Start a new game with the same settings
    start_game(category, difficulty)

    # Return empty response with 204 No Content status
    return ('', 204)
 

# Start the Flask development server when this script is run directly
if __name__ == '__main__':
    app.run(debug=True)
