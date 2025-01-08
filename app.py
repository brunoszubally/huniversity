from flask import Flask, jsonify, request
import requests
import urllib3
from datetime import datetime
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ssl

urllib3.disable_warnings()

app = Flask(__name__)

# Alapértelmezett értékek
DEFAULT_VALUES = {
    'apiKulcs': 'Hv-Tst-t312-r34q-v921-5318c',
    'azonosito': '1223433576',
    'intezmenyRovidNev': 'KOSSUTH LAJOS ÁLTALÁNOS ISKOLA',
    'intezmenyTelepules': 'GYÖNGYÖSPATA',
    'elonev': '',
    'keresztnev': 'Ádám',
    'vezeteknev': 'Misuta',
    'lakohelyTelepules': 'GYÖNGYÖS',
    'munkarend': 'Nappali',
    'neme': 'Ferfi',
    'oktazon': '76221103192',
    'szuletesiEv': 2010
}

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/wsdl', methods=['GET'])
def get_wsdl():
    url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/xml,application/xml',
        'Cache-Control': 'no-cache'
    }
    
    try:
        response = requests.get(
            url, 
            headers=headers,
            verify=False,
            timeout=30
        )
        
        return jsonify({
            "status": "success",
            "http_status": response.status_code,
            "headers": dict(response.headers),
            "content_length": len(response.content),
            "content_type": response.headers.get('content-type', ''),
            "content": response.text[:1000] if response.status_code == 200 else None
        })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e))
        }), 500

@app.route('/check-student', methods=['GET', 'POST'])
def check_student():
    try:
        # Session beállítása retry logikával
        session = Session()
        
        # TLS adapter hozzáadása
        adapter = TLSAdapter()
        session.mount('https://', adapter)
        
        # Retry stratégia
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        
        # Session beállítások
        session.verify = False
        session.timeout = (5, 30)  # (connect timeout, read timeout)
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'text/xml;charset=UTF-8',
            'Accept': 'text/xml,application/xml',
            'Connection': 'keep-alive'
        }

        transport = Transport(session=session)
        settings = Settings(
            strict=False,
            xml_huge_tree=True,
            force_https=True
        )

        # WSDL betöltése
        print("Loading WSDL...")
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        client = Client(
            wsdl_url,
            transport=transport,
            settings=settings
        )
        print("WSDL loaded successfully")

        # Ha van POST body, használjuk azt, egyébként az alapértelmezett értékeket
        data = request.get_json() if request.is_json else {}
        
        print("Calling SOAP service...")
        result = client.service.DiakigazolvanyJogosultsagLekerdezes(
            ApiKulcs=data.get('apiKulcs', DEFAULT_VALUES['apiKulcs']),
            Azonosito=data.get('azonosito', DEFAULT_VALUES['azonosito']),
            IntezmenyRovidNev=data.get('intezmenyRovidNev', DEFAULT_VALUES['intezmenyRovidNev']),
            IntezmenyTelepules=data.get('intezmenyTelepules', DEFAULT_VALUES['intezmenyTelepules']),
            JogosultNev={
                'Elonev': data.get('elonev', DEFAULT_VALUES['elonev']),
                'Keresztnev': data.get('keresztnev', DEFAULT_VALUES['keresztnev']),
                'Vezeteknev': data.get('vezeteknev', DEFAULT_VALUES['vezeteknev'])
            },
            LakohelyTelepules=data.get('lakohelyTelepules', DEFAULT_VALUES['lakohelyTelepules']),
            Munkarend=data.get('munkarend', DEFAULT_VALUES['munkarend']),
            Neme=data.get('neme', DEFAULT_VALUES['neme']),
            Oktazon=data.get('oktazon', DEFAULT_VALUES['oktazon']),
            SzuletesiEv=data.get('szuletesiEv', DEFAULT_VALUES['szuletesiEv'])
        )
        print("SOAP call completed")
        
        return jsonify({
            "status": "success",
            "response": result,
            "used_values": {
                "apiKulcs": data.get('apiKulcs', DEFAULT_VALUES['apiKulcs']),
                "azonosito": data.get('azonosito', DEFAULT_VALUES['azonosito']),
                "intezmenyRovidNev": data.get('intezmenyRovidNev', DEFAULT_VALUES['intezmenyRovidNev']),
                "intezmenyTelepules": data.get('intezmenyTelepules', DEFAULT_VALUES['intezmenyTelepules']),
                "elonev": data.get('elonev', DEFAULT_VALUES['elonev']),
                "keresztnev": data.get('keresztnev', DEFAULT_VALUES['keresztnev']),
                "vezeteknev": data.get('vezeteknev', DEFAULT_VALUES['vezeteknev']),
                "lakohelyTelepules": data.get('lakohelyTelepules', DEFAULT_VALUES['lakohelyTelepules']),
                "munkarend": data.get('munkarend', DEFAULT_VALUES['munkarend']),
                "neme": data.get('neme', DEFAULT_VALUES['neme']),
                "oktazon": data.get('oktazon', DEFAULT_VALUES['oktazon']),
                "szuletesiEv": data.get('szuletesiEv', DEFAULT_VALUES['szuletesiEv'])
            }
        })
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e)),
            "details": str(getattr(e, 'detail', ''))
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 