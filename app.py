from flask import Flask, jsonify
from zeep import Client
from zeep.transports import Transport
from requests import Session
import logging.config

app = Flask(__name__)

# SOAP debug logging beállítása
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

@app.route('/check', methods=['GET'])
def check_student():
    try:
        session = Session()
        client = Client(
            'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc',
            transport=Transport(session=session)
        )

        # Szolgáltatás hívása fix teszt azonosítóval
        result = client.service.Ellenoriz(
            apiKulcs='Hv-Tst-t312-r34q-v921-5318c',
            oktatasiAzonosito='76221103192'  # Fix teszt azonosító
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
