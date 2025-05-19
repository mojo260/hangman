from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'hangman-secret'  # Needed for session management

# List of possible words to guess
words = ['banana', 'computer', 'python', 'hangman', 'keyboard']

# Initializes a new game
def start_game():
    word = random.choice(words)
    session['word'] = word
    session['guesses'] = []
    session['lives'] = 6

@app.route('/')
def index():
    # Start a game if one doesn't already exist
    if 'word' not in session:
        start_game()
    return render_template('index.html')

@app.route('/guess', methods=['POST'])
def guess():
    letter = request.form['letter'].lower()
    word = session.get('word', '')
    guesses = session.get('guesses', [])
    lives = session.get('lives', 6)

    # If the guess is new and valid
    if letter and letter not in guesses:
        guesses.append(letter)
        if letter not in word:
            lives -= 1  # Wrong guess, lose a life

    # Save the updated game state
    session['guesses'] = guesses
    session['lives'] = lives

    # Build the displayed word with underscores
    display_word = ''.join([c if c in guesses else '_' for c in word])

    # Game end logic
    game_over = lives == 0 or '_' not in display_word
    wrong_guesses = len([g for g in guesses if g not in word])

    return jsonify({
        'display_word': display_word,
        'guesses': guesses,
        'lives': lives,
        'game_over': game_over,
        'won': '_' not in display_word,
        'stage': min(wrong_guesses + 1, 7)  # stage1.png to stage7.png
    })

@app.route('/reset', methods=['POST'])
def reset():
    start_game()
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
