import json
import os

from flask import Flask, request, jsonify

from document_delivery_service.service import doc_service_callback

app = Flask(__name__)

@app.route("/", methods=['POST'])
def hello_world():

    data = request.get_data()
    json_data = json.loads(data.decode('utf-8'))
    print (json_data)
    doc_service_callback(ce = None, alt = json_data)

    return jsonify({"status": "OK"})


if __name__ == '__main__':
    app.run(port=os.getenv('OIDC_TOKEN_URL', '8080'), debug=True)
