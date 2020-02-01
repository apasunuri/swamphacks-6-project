from flask import Flask, render_template

app = Flask(__name__)

polyline = "ii|sDpjwuNqDAcIAgCA]?w@?wBAc@AgAAyAAiBCK?aAA_A?eAA_A?iAAwB?m@AiC?Q?_C@Y@S?eA?M@eA@"

start_point = {
    'lat' : 29.64133,
    'lng' : -82.37241
}

@app.route("/")
def main():
    return "Hello World"

@app.route("/map")
def map():
    return render_template('map.html', start_point=start_point, polyline=polyline)
    
if __name__ == "__main__":
    app.run(debug=True)
    