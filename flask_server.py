from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/prime', methods=['POST'])
def get_temperature():
    query = request.json.get('temp',"NA")
    print(query)

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True,port=6464)