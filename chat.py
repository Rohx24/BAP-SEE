import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load intents from JSON file
with open('//Users//rohitdiggi//Downloads//BAP//intents.json', 'r') as file:
    intents = json.load(file)

# Load pre-trained model and other data
FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

# Initialize model
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# Bot name
bot_name = "Sam"

# Define conversation state variables
context = None
symptoms = None

# Function to check if a symptom pattern is contained in the user's message
def find_matching_symptom(message):
    matched_symptoms = []
    for intent in intents['intents']:
        if intent["tag"] == "symptoms":
            for pattern in intent['patterns']:
                if pattern.lower() in message.lower():
                    matched_symptoms.append(pattern)
    return matched_symptoms

def save_location(location):
    # Define variations of phrases indicating location
    location_keywords = ["i live in", "i live at", "i am at"]
    
    # Extract the location from the user input
    for keyword in location_keywords:
        if keyword in location.lower():
            location = location.lower().replace(keyword, "").strip()
            break  # Stop loop once the location is found
    
    # Save the location to the file
    with open("loc.txt", "w") as file:
        file.write(location)


def get_response(msg):
    global context, symptoms
    
    # Tokenize user input
    sentence = tokenize(msg)
    
    # Bag of words representation
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    # Get model prediction
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    # Calculate confidence
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    # Check confidence level and retrieve appropriate response
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                # Greeting
                if tag == "greeting":
                    return random.choice(intent['responses'])
                # Emergency, distress, healthcare, or appointments
                elif tag in ["emergency", "distress", "healthcare", "appointments"]:
                    return random.choice(intent['responses'])
                # Intro
                elif tag == "intro":
                    return "I am your Virtual AI assistant, here to help you with Healthcare services."
                # Location
                elif tag == "location":
                    context = "location"
                    save_location(msg)  # Save location
                    return "Your location has been noted. What symptoms are you facing?"
                elif tag == "ok":
                    return "Is there anything else I can do for you?"
                elif tag == "conclusion":
                    return "Until next time! Take care."
                elif tag == "medications":
                    return random.choice(intent['responses'])
                elif tag == "insurance":
                    return random.choice(intent['responses'])
                elif tag == "mental_health":
                    return random.choice(intent['responses'])
                elif tag == "goodbye":
                    return random.choice(intent['responses'])
                # Symptoms
                elif tag == "symptoms":
                    if context == "location":
                        symptoms = find_matching_symptom(msg)  # Find matching symptoms
                        context = None  # Reset context
                        
                        # If symptoms found, return the corresponding response
                        if symptoms:
                            for symptom in symptoms:
                                for pattern, response in zip(intent['patterns'], intent['responses']):
                                    if symptom.lower() == pattern.lower():
                                        response = response + " Do you need further assistance?"
                                        return response
                            # If no matching response found, provide a generic response
                            return "It seems like you're experiencing symptoms beyond what I can understand. Please consult a doctor for proper diagnosis and treatment. Do you need further assistance?"
                    else:
                        return "Please provide better details to help me better understand"

    # If no appropriate response is found, return a generic message
    return "I'm sorry, I couldn't understand your request. Please provide more information."