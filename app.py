from flask import request, jsonify, Flask, make_response, render_template
from forms import SearchForm
import connections
import sql

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/search', methods=['GET'])
def search():
    source = request.args.get('source')
    destination = request.args.get('destination')
    passengers = int(request.args.get('passengers', 1))
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    results = connections.find_all(source, destination, passengers, date_from, date_to)
    return jsonify(results)


@app.route('/search/user', methods=['GET', 'POST'])
def user_search():
    form = SearchForm(csrf_enabled=False)
    if form.validate_on_submit():
        source = request.form.get('source')
        destination = request.form.get('destination')
        passengers = int(request.form.get('passengers'))
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')
        journeys = connections.find_all(source, destination, passengers, date_from, date_to)
        print(journeys)
        for day in journeys:
            for journey in day:
                print(journey)
                sql.save_into_db(journey)
        template = render_template('results.html', connections=journeys)
        return make_response(template)
    else:
        return render_template('search.html', form=form)


@app.route('/locations-search', methods=['GET'])
def locations_search():
    term = request.args.get('term', '').lower()
    destinations = connections.cities_list()
    return jsonify([x for x in destinations if term in x.lower()])


if __name__ == '__main__':
    app.run(debug=True)
