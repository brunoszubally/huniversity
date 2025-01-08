from flask import Flask, jsonify
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
import urllib3

urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        session = Session()
        session.verify = False
        session.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': 'http://www.oktatas.hu/Keres'
        }
        
        # WSDL és végpont külön kezelése
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        service_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc'
        
        settings = Settings(strict=False)
        
        client = Client(
            wsdl_url,
            transport=Transport(session=session),
            settings=settings
        )
        
        service = client.create_service(
            binding_name='{http://www.oktatas.hu/}BasicHttpBinding_IPublicServices',
            address=service_url
        )

        # A példában szereplő formátumot követjük
        result = service.Keres(
            ApiKulcs='TESZT',
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
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e)),
            "details": str(getattr(e, 'detail', ''))
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
