from flask import Flask, jsonify
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
import urllib3
import logging.config

# Logging beállítása
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
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

urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        # Session beállítása részletes hibakezeléssel
        session = Session()
        session.verify = False
        session.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'text/xml;charset=UTF-8',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        
        # Explicit timeout beállítása
        session.timeout = 30
        
        transport = Transport(session=session, timeout=30, operation_timeout=20)
        
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        
        # Debug információk kiírása
        print(f"Connecting to WSDL: {wsdl_url}")
        
        settings = Settings(
            strict=False,
            xml_huge_tree=True,
            force_https=False
        )

        client = Client(
            wsdl_url,
            transport=transport,
            settings=settings
        )

        print("WSDL loaded successfully")
        print("Available operations:", [op for op in client.service._operations.keys()])

        result = client.service.DiakigazolvanyJogosultsagLekerdezes(
            ApiKulcs='Hv-Tst-t312-r34q-v921-5318c',
            Azonosito='1223433576',
            IntezmenyRovidNev='KOSSUTH LAJOS ÁLTALÁNOS ISKOLA',
            IntezmenyTelepules='GYÖNGYÖSPATA',
            JogosultNev={
                'Elonev': '',
                'Keresztnev': 'Ádám',
                'Vezeteknev': 'Misuta'
            },
            LakohelyTelepules='GYÖNGYÖS',
            Munkarend='Nappali',
            Neme='Ferfi',
            Oktazon='76221103192',
            SzuletesiEv=2010
        )
        
        return jsonify({
            "status": "success",
            "response": result
        })
        
    except Exception as e:
        error_details = {
            "status": "error",
            "message": str(e),
            "error_type": str(type(e)),
            "details": str(getattr(e, 'detail', '')),
            "request_info": {
                "url": wsdl_url,
                "headers": dict(session.headers)
            }
        }
        print("Error details:", error_details)
        return jsonify(error_details), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
