from flask import Flask, jsonify
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# SSL figyelmeztetések kikapcsolása
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        # Session beállítása retry logikával
        session = Session()
        retry_strategy = Retry(
            total=5,  # összes próbálkozás
            backoff_factor=0.5,  # várakozási idő a próbálkozások között
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # SSL és timeout beállítások
        session.verify = False
        session.timeout = (5, 30)  # (connect timeout, read timeout)
        
        # SOAP kliens beállítások
        settings = Settings(strict=False, xml_huge_tree=True)
        
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        client = Client(
            wsdl_url,
            transport=Transport(session=session),
            settings=settings
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
            "error_type": str(type(e)),
            "details": str(getattr(e, 'detail', ''))  # SOAP hiba részletek
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
