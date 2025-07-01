from flask import Flask, request, jsonify, send_file
from flask_cors import CORS # Die ist wichtig, damit deine Webseite mit dem Server quatschen kann

# Deine Flask-App wird gestartet
app = Flask(__name__)
CORS(app) # Und hier sorgen wir direkt dafür, dass die Kommunikation reibungslos läuft

# Das ist jetzt die Haupt-Adresse deines Tools. Wenn jemand die aufruft, kommt deine Webseite!
@app.route('/')
def serve_index_html():
    return send_file('index.html')

# Das hier ist deine Funktion, die die Bewertungen berechnet – die bleibt, wie sie ist.
@app.route('/calculate_average', methods=['POST'])
def calculate_average_api():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'Keine JSON-Daten im Request Body gefunden.'}), 400

        criteria = data.get('criteria', [])
        main_topic = data.get('mainTopic', 'Unbenanntes Thema')

        if not isinstance(criteria, list):
            return jsonify({'success': False, 'error': 'Das Feld "criteria" muss eine Liste sein.'}), 400

        total = 0
        count = 0
        results_details = []
        invalid_ratings_found = False

        for item in criteria:
            if not isinstance(item, dict):
                invalid_ratings_found = True
                continue

            name = item.get('name', 'Unbenanntes Kriterium')
            rating = item.get('rating')

            if isinstance(rating, int) and 1 <= rating <= 6:
                total += rating
                count += 1
                results_details.append({"name": name, "rating": rating})
            else:
                invalid_ratings_found = True
                results_details.append({"name": name, "rating": rating, "status": "Ungültige Bewertung"})

        if count > 0:
            average = round(total / count, 2)
            response_message = f"Durchschnittliche Bewertung für '{main_topic}': {average}"
            return jsonify({
                'success': True,
                'message': response_message,
                'average_rating': average,
                'topic': main_topic,
                'evaluated_criteria': results_details,
                'warnings': "Einige Bewertungen waren ungültig und wurden ignoriert." if invalid_ratings_found else None
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': "Keine gültigen Bewertungen gefunden. Bitte stelle sicher, dass 'criteria' eine Liste von Objekten mit 'name' und 'rating' ist (rating 1-6).",
                'topic': main_topic,
                'evaluated_criteria': results_details,
                'error': "Keine gültigen Bewertungen zum Berechnen gefunden."
            }), 400

    except Exception as e:
        # Falls mal was schiefgeht, sehen wir hier, was los war.
        print(f"Fehler bei der Berechnung der Bewertung: {e}")
        return jsonify({'success': False, 'error': f'Interner Serverfehler: {str(e)}'}), 500

# Das hier ist nur zum lokalen Testen auf deinem PC, Render nutzt das nicht direkt.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')