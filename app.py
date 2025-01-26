from flask import Flask, jsonify, request
import requests
import urllib3
from datetime import datetime

# SSL figyelmeztetések letiltása
urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check-student', methods=['GET'])
def check_student():
    try:
        # Azonosító lekérése a query paraméterből - kötelező paraméter
        azonosito = request.args.get('azonosito')
        
        if not azonosito:
            return jsonify({
                "status": "error",
                "message": "Az 'azonosito' paraméter megadása kötelező"
            }), 400
            
        # SOAP kérés XML sablon dinamikus azonosítóval
        soap_request = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/" xmlns:okt1="http://www.oktatas.hu">
            <soapenv:Header/>
            <soapenv:Body>
                <okt:Keres>
                    <okt1:ApiKulcs>Hv-Tst-t312-r34q-v921-5318c</okt1:ApiKulcs>
                    <okt1:Azonosito>{azonosito}</okt1:Azonosito>
                </okt:Keres>
            </soapenv:Body>
        </soapenv:Envelope>
        '''

        # SOAP kérés küldése
        url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc'
        
        headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': 'http://www.oktatas.hu/IPublicServices/DiakigazolvanyJogosultsagLekerdezes',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/xml, application/xml'
        }

        response = requests.post(
            url=url,
            data=soap_request.encode('utf-8'),
            headers=headers,
            verify=False,
            timeout=30
        )

        # XML válasz feldolgozása és egyszerűsített válasz visszaadása
        if 'KedvezmenyreJogosult' in response.text:
            return jsonify({"status": "success", "code": 1})
        elif 'KedvezmenyreNemJogosult' in response.text:
            return jsonify({"status": "success", "code": 2})
        elif 'NemLetezoKartya' in response.text:
            return jsonify({"status": "success", "code": 3})
        else:
            return jsonify({"status": "error", "code": 0, "message": "Ismeretlen válasz"})

    except Exception as e:
        return jsonify({
            "status": "error",
            "code": 0,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)