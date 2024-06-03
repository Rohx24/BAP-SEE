from flask import Flask, render_template, request, jsonify
from chat import get_response, bot_name

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['user_message']
    bot_response = get_response(user_message)
    return jsonify({'bot_response': bot_response})

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=3000)
