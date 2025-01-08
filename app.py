from flask import Flask, jsonify
from zeep import Client
from zeep.transports import Transport
from requests import Session

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        session = Session()
        session.verify = False
        
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        client = Client(
            wsdl_url,
            transport=Transport(session=session)
        )

        # AuthInfo objektum létrehozása
        auth_info = {
            'ApiKey': 'Hv-Tst-t312-r34q-v921-5318c'
        }

        # Request objektum létrehozása a példa alapján
        request = {
            'Azonosito': '1223433576',
            'IntezmenyRovidNev': 'KOSSUTH LAJOS ÁLTALÁNOS ISKOLA',
            'IntezmenyTelepules': 'GYÖNGYÖSPATA',
            'JogosultNev': {
                'Elonev': '',
                'Keresztnev': 'Ádám',
                'Vezeteknev': 'Misuta'
            },
            'LakohelyTelepules': 'GYÖNGYÖS',
            'Munkarend': 'Nappali',
            'Neme': 'Ferfi',
            'Oktazon': '76221103192',
            'SzuletesiEv': 2010
        }

        # A helyes paraméterstruktúrával hívjuk meg
        result = client.service.CheckJogosultsag(
            authInfo=auth_info,
            request=request
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
