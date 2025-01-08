from flask import Flask, jsonify
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# SSL figyelmeztetések kikapcsolása
urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        # Session létrehozása retry logikával
        session = Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[408, 429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Proxy beállítások (ha szükséges)
        proxies = {
            'http': 'http://proxy.example.com:8080',
            'https': 'http://proxy.example.com:8080'
        }
        session.proxies = proxies
        
        session.verify = False
        session.timeout = 60
        
        # További HTTP fejlécek
        session.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # SOAP kliens beállítások
        settings = Settings(
            strict=False,
            xml_huge_tree=True,
            raw_response=True
        )
        
        client = Client(
            'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc?wsdl',
            transport=Transport(session=session),
            settings=settings
        )

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
