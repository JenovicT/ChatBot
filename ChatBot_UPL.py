from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

# Initialiser l'application Flask
app = Flask(__name__)

# Configurez la clé API OpenAI via une variable d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

# Réponses basiques spécifiques à UPL
def get_upl_response(question):
    faq = {
        "adresse de l'université": "L'Université UPL se trouve au 123 Rue de l'Éducation, Ville UPL.",
        "frais d'inscription": "Les frais d'inscription pour l'année 2025 sont de 500 €.",
        "cours disponibles": "Les cours disponibles incluent Informatique, Mathématiques, Biologie, et Gestion.",
        "heures d'ouverture": "L'université est ouverte de 8h à 18h, du lundi au vendredi.",
    }
    return faq.get(question.lower(), None)

# Gérer les messages entrants via WhatsApp
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    response = MessagingResponse()
    msg = response.message()

    # Vérifier si la question est dans la FAQ locale
    answer = get_upl_response(incoming_msg)
    if answer:
        msg.body(answer)
    else:
        # Utiliser OpenAI pour des réponses plus complexes
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": incoming_msg}]
            )
            msg.body(completion.choices[0].message['content'].strip())
        except Exception as e:
            msg.body("Désolé, je ne peux pas répondre à cette question pour le moment.")

    return str(response)

# Exécuter l'application si elle est lancée localement
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=int(os.getenv("PORT", 5000)))
