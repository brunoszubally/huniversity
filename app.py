from flask import Flask, jsonify
from zeep import Client
from zeep.transports import Transport
from requests import Session
import urllib3

# SSL figyelmeztetések kikapcsolása (csak fejlesztéshez)
urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        # Session létrehozása
        session = Session()
        session.verify = False
        
        # SOAP kliens létrehozása a dokumentációban szereplő címmel
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc?wsdl'
        client = Client(
            wsdl_url,
            transport=Transport(session=session)
        )

        # Ellenőrzés a teszt adatokkal
        result = client.service.Ellenoriz(
            apiKulcs='Hv-Tst-t312-r34q-v921-5318c',
            oktatasiAzonosito='76221103192'
        )
        
        return jsonify({
            "status": "success",
            "response": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e))
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
