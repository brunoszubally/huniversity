from flask import Flask, jsonify, request
import requests
import urllib3
from datetime import datetime
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
import os

urllib3.disable_warnings()

app = Flask(__name__)

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

@app.route('/check-student', methods=['POST'])
def check_student():
    try:
        session = Session()
        session.verify = False
        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'text/xml;charset=UTF-8',
            'Accept': 'text/xml,application/xml'
        }

        transport = Transport(session=session, timeout=30)
        
        settings = Settings(
            strict=False,
            xml_huge_tree=True
        )

        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        client = Client(
            wsdl_url,
            transport=transport,
            settings=settings
        )

        # Request adatok a POST body-ból
        data = request.get_json()
        
        result = client.service.DiakigazolvanyJogosultsagLekerdezes(
            ApiKulcs=data.get('apiKulcs', 'Hv-Tst-t312-r34q-v921-5318c'),
            Azonosito=data.get('azonosito', '1223433576'),
            IntezmenyRovidNev=data.get('intezmenyRovidNev', 'KOSSUTH LAJOS ÁLTALÁNOS ISKOLA'),
            IntezmenyTelepules=data.get('intezmenyTelepules', 'GYÖNGYÖSPATA'),
            JogosultNev={
                'Elonev': data.get('elonev', ''),
                'Keresztnev': data.get('keresztnev', 'Ádám'),
                'Vezeteknev': data.get('vezeteknev', 'Misuta')
            },
            LakohelyTelepules=data.get('lakohelyTelepules', 'GYÖNGYÖS'),
            Munkarend=data.get('munkarend', 'Nappali'),
            Neme=data.get('neme', 'Ferfi'),
            Oktazon=data.get('oktazon', '76221103192'),
            SzuletesiEv=data.get('szuletesiEv', 2010)
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
    app.run(debug=True) 