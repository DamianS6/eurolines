from flask import request, jsonify, Flask
import connections

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/search', methods=['GET'])
def search():
    source = request.args.get('source')
    destination = request.args.get('destination')
    passengers = int(request.args.get('passengers', 1))
    departure_date = request.args.get('departure_date')
    results = connections.find_connection(source, destination, departure_date, passengers)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
