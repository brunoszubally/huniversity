from flask import Flask, jsonify, request
import requests
import urllib3
from datetime import datetime
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

if __name__ == '__main__':
    app.run(debug=True) 