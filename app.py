from flask import Flask, jsonify
import requests
import urllib3
import xml.etree.ElementTree as ET
from datetime import datetime

urllib3.disable_warnings()

app = Flask(__name__)

def get_wsdl_info():
    url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/xml,application/xml'
    }
    
    response = requests.get(
        url=url,
        headers=headers,
        verify=False,
        timeout=30
    )
    
    if response.status_code == 200:
        # Parse WSDL
        root = ET.fromstring(response.content)
        
        # WSDL namespace-ek
        namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xs': 'http://www.w3.org/2001/XMLSchema'
        }
        
        # Műveletek keresése
        operations = []
        for operation in root.findall('.//wsdl:operation', namespaces):
            operations.append(operation.attrib['name'])
            
        return {
            "operations": operations,
            "raw_wsdl": response.text[:1000]  # első 1000 karakter a WSDL-ből
        }
    return None

@app.route('/analyze-wsdl', methods=['GET'])
def analyze_wsdl():
    try:
        wsdl_info = get_wsdl_info()
        return jsonify({
            "status": "success",
            "wsdl_info": wsdl_info
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e))
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 