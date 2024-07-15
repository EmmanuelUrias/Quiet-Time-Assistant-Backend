from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv
import os
from flask_cors import CORS


# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Assistant ID
assistant_id = os.getenv('ASSISTANT_ID')

# Function to handle OpenAI assistant response
async def get_assistant_response(message):

    # Create a thread
    thread = openai.beta.threads.create()

    # Send a message to the thread
    message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
    )

    # Run the assistant with specific instructions
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions="Refer to the user as a fellow disciple and be friendly in your response",
    )

    if run.status == "completed":
        messages = openai.beta.threads.messages.list(thread_id=thread.id)

        for message in messages:
            if message.content[0].type == "text":
                assistant_response = message.content[0].text.value
                return assistant_response
    return None

# Route for sending messages
@app.route('/send_message', methods=['POST'])
async def send_message():
    data = request.get_json()
    user_message = data.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Handle the message asynchronously
    assistant_response = await handle_message(user_message)
    if assistant_response == False:
        return jsonify({"status": "Message failed", "response": "Oops there was an error please try again or wait for another time"}), 500
    return jsonify({"status": "Message received and processed", "response": assistant_response}), 200

# Function to handle the message
async def handle_message(message):
    assistant_response = await get_assistant_response(message)
    # Here you can handle the response, for example, log it or send it to another service
    if assistant_response == None:
        return False
    return assistant_response

if __name__ == '__main__':
    app.run(debug=True)
