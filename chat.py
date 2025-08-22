from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import datetime
import random
import wikipedia
import sympy as sp
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

class AIAssistant:
    def _init_(self):
        # Free joke API
        self.joke_api = "https://official-joke-api.appspot.com/random_joke"
        
        # OpenWeatherMap API info — Replace with your actual free API key
        self.weather_api = "http://api.openweathermap.org/data/2.5/weather"
        self.weather_api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # Put your OpenWeatherMap free API key here
        
        # Knowledge base for quick responses
        self.knowledge_base = {
            'capitals': {
                'france': 'Paris',
                'germany': 'Berlin',
                'italy': 'Rome',
                'spain': 'Madrid',
                'uk': 'London',
                'united kingdom': 'London',
                'usa': 'Washington D.C.',
                'united states': 'Washington D.C.',
                'india': 'New Delhi',
                'china': 'Beijing',
                'japan': 'Tokyo',
                'australia': 'Canberra',
                'canada': 'Ottawa',
                'brazil': 'Brasília',
                'russia': 'Moscow',
                'mexico': 'Mexico City'
            },
            'historical_facts': {
                'world war 1': 'World War I (1914-1918) was a global conflict primarily in Europe, triggered by the assassination of Archduke Franz Ferdinand.',
                'world war 2': 'World War II (1939-1945) was the deadliest conflict in human history, involving most of the world\'s nations.',
                'cold war': 'The Cold War (1947-1991) was a period of tension between the US and Soviet Union.',
                'industrial revolution': 'The Industrial Revolution (1760-1840) marked the transition to mechanized manufacturing.',
                'french revolution': 'The French Revolution (1789-1799) was a period of radical social and political change in France.'
            },
            'geographical_facts': {
                'largest country': 'Russia is the largest country by land area (17.1 million km²)',
                'smallest country': 'Vatican City is the smallest country (0.17 square miles)',
                'longest river': 'The Nile River is the longest river in the world (6,650 km)',
                'highest mountain': 'Mount Everest is the highest mountain (8,848.86 m)',
                'largest ocean': 'The Pacific Ocean is the largest ocean'
            }
        }

    def get_current_time(self):
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')} on {now.strftime('%Y-%m-%d')}"

    def get_current_date(self):
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"

    def solve_math(self, expression):
        try:
            # Clean expression to numbers and math symbols
            expression = re.sub(r'[^0-9+\-*/().\s^]', '', expression)
            expression = expression.replace('^', '')  # correct exponent symbol
            
            # Use sympy for symbolic math parsing
            try:
                result = sp.sympify(expression)
                return f"The answer is: {result}"
            except:
                # fallback to Python eval
                result = eval(expression)
                return f"The answer is: {result}"
        except:
            return "I couldn't solve that mathematical expression. Please check your syntax."

    def get_joke(self):
        try:
            response = requests.get(self.joke_api, timeout=5)
            if response.status_code == 200:
                joke_data = response.json()
                return f"{joke_data['setup']} {joke_data['punchline']} 😄"
        except:
            pass
        
        fallback_jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "Why did the math book look so sad? Because it had too many problems! 📚",
            "What do you call a fake noodle? An impasta! 🍝",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚",
            "What do you call a sleeping bull? A bulldozer! 🐂"
        ]
        return random.choice(fallback_jokes)

    def get_weather(self, city="London"):
        if not self.weather_api_key or self.weather_api_key == "YOUR_OPENWEATHERMAP_API_KEY":
            return "Weather feature requires a free API key from OpenWeatherMap. For now, it's a beautiful day! ☀"
        try:
            url = f"{self.weather_api}?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                return f"The weather in {city.title()} is {desc} with a temperature of {temp}°C."
            else:
                return "Sorry, I couldn't fetch the weather for that city."
        except:
            return "I couldn't fetch the weather right now. Please try again later."

    def search_wikipedia(self, query):
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(query, sentences=2, auto_suggest=True)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            try:
                summary = wikipedia.summary(e.options[0], sentences=2)
                return summary
            except:
                return f"I found multiple topics related to '{query}'. Could you be more specific?"
        except wikipedia.exceptions.PageError:
            return f"I couldn't find information about '{query}' on Wikipedia."
        except:
            return "I'm having trouble accessing Wikipedia right now."

    def analyze_sentiment(self, text):
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                return "That sounds positive! 😊"
            elif polarity < -0.1:
                return "That sounds negative. I hope things get better! 😔"
            else:
                return "That sounds neutral to me."
        except:
            return "I couldn't analyze the sentiment of that text."

    def handle_geography(self, message):
        message_lower = message.lower()
        if 'capital' in message_lower:
            for country, capital in self.knowledge_base['capitals'].items():
                if country in message_lower:
                    return f"The capital of {country.title()} is {capital}."
            return "Please specify a country to get its capital."
        for fact, answer in self.knowledge_base['geographical_facts'].items():
            if any(word in message_lower for word in fact.split()):
                return answer
        return None

    def handle_history(self, message):
        message_lower = message.lower()
        for event, info in self.knowledge_base['historical_facts'].items():
            if event in message_lower:
                return info
        return None

    def handle_politics(self, message):
        message_lower = message.lower()
        political_responses = {
            'democracy': 'Democracy is a form of government where power is held by the people, either directly or through elected representatives.',
            'republic': 'A republic is a form of government where the country is considered a "public matter" and officials are elected.',
            'president': 'A president is typically the head of state in a republic.',
            'parliament': 'Parliament is a legislative body of government, typically in democratic systems.',
            'constitution': 'A constitution is the fundamental law that establishes the framework of government.'
        }
        for term, definition in political_responses.items():
            if term in message_lower:
                return definition
        return None

    def process_message(self, message):
        message_lower = message.lower()
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm your AI assistant. How can I help you today? 😊"
        
        # Time queries
        if 'time' in message_lower:
            return self.get_current_time()
        
        # Date queries
        if any(word in message_lower for word in ['date', 'today', 'day']):
            return self.get_current_date()
        
        # Math queries
        if any(word in message_lower for word in ['solve', 'calculate', 'math']) or re.search(r'[\d+\-*/()^]', message):
            return self.solve_math(message)
        
        # Jokes
        if 'joke' in message_lower:
            return self.get_joke()
        
        # Weather queries
        if 'weather' in message_lower:
            city_match = re.search(r'weather in (\w+)', message_lower)
            city = city_match.group(1) if city_match else "London"
            return self.get_weather(city)
        
        # Name queries
        if any(phrase in message_lower for phrase in ['your name', 'who are you', 'what are you']):
            return "I'm your AI Assistant! I can help with math, geography, history, general questions, and casual conversation. 🤖"
        
        # Geography
        geography_response = self.handle_geography(message)
        if geography_response:
            return geography_response
        
        # History
        history_response = self.handle_history(message)
        if history_response:
            return history_response
        
        # Politics
        politics_response = self.handle_politics(message)
        if politics_response:
            return politics_response
        
        # Sentiment analysis on emotional keywords
        if any(word in message_lower for word in ['feel', 'sad', 'happy', 'angry', 'excited']):
            return self.analyze_sentiment(message)
        
        # Wikipedia quick search for short queries without common question words
        if len(message.split()) <= 5 and not any(word in message_lower for word in ['how', 'why', 'when', 'where']):
            wiki_result = self.search_wikipedia(message)
            if "I couldn't find" not in wiki_result and "I found multiple" not in wiki_result:
                return wiki_result
        
        # Default fallback
        default_responses = [
            "That's an interesting question! I'll do my best to help you with the information I have.",
            "I'd be happy to help! Could you provide more details about what you're looking for?",
            "Great question! Let me think about that. Could you be more specific?",
            "I'm here to help! Feel free to ask me about math, geography, history, or just chat!",
            "Interesting! While I might not have all the details, I'm happy to discuss what I know about this topic."
        ]
        return random.choice(default_responses)

# Instantiate assistant
ai_assistant = AIAssistant()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        response = ai_assistant.process_message(message)
        return jsonify({
            'response': response,
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        # For debugging, you can print(e)
        return jsonify({
            'error': 'An error occurred processing your message.',
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'features': [
            'General conversation',
            'Mathematics solving',
            'Geography questions',
            'Historical facts',
            'Political information',
            'Time and date',
            'Jokes and entertainment',
            'Weather (with API key)',
            'Wikipedia search',
            'Sentiment analysis'
        ]
    })

@app.route('/api/capabilities', methods=['GET'])
def capabilities():
    return jsonify({
        'capabilities': {
            'mathematics': 'Solve equations, calculations, basic algebra',
            'geography': 'Country capitals, geographical facts',
            'history': 'Historical events, dates, facts',
            'politics': 'Basic political definitions and concepts',
            'general_knowledge': 'Wikipedia-based information',
            'conversation': 'Casual chat, greetings, jokes',
            'utilities': 'Time, date, weather (with API key)',
            'sentiment': 'Basic sentiment analysis'
        },
        'supported_apis': [
            'Wikipedia',
            'OpenWeatherMap (requires free API key)',
            'Official Joke API'
        ]
    })

if __name__ == '_main_':
    print("🤖 AI Chatbot Backend Starting...")
    print("📊 Available endpoints:")
    print("   POST /api/chat - Main chat endpoint")
    print("   GET /api/health - Health check")
    print("   GET /api/capabilities - Bot capabilities")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)