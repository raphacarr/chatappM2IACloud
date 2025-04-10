import boto3
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les clés depuis les variables d'environnement
session = boto3.Session(
   aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
   aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
   region_name=os.getenv('AWS_REGION')
)
comprehend = session.client('comprehend')

def get_sentiment(text):
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    return response['Sentiment']

texte = "I am working with AWS services and i hate it."
print(get_sentiment(texte))