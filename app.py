from flask import Flask, jsonify, request
import requests
import urllib3
from datetime import datetime

# SSL figyelmeztetések letiltása
urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "success",
        "message": "pong",
        "timestamp": datetime.now().isoformat()
    })

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

        # Validáció: ha nem 10 karakter ÉS nem 0-val vagy 1-gyel kezdődik
        if len(azonosito) != 10 and not (azonosito.startswith('0') or azonosito.startswith('1')):
            return jsonify({
                "status": "error",
                "code": 4,
                "message": "Érvénytelen azonosító formátum"
            }), 400

        # SOAP kérés XML sablon dinamikus azonosítóval
        soap_request = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/" xmlns:okt1="http://www.oktatas.hu">
            <soapenv:Header/>
            <soapenv:Body>
                <okt:Keres>
                    <okt1:ApiKulcs>Hv-Lve-l428-s67t-c156-2465b</okt1:ApiKulcs>
                    <okt1:Azonosito>{azonosito}</okt1:Azonosito>
                </okt:Keres>
            </soapenv:Body>
        </soapenv:Envelope>
        '''

        # SOAP kérés küldése
        url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-live/publicservices.svc'
        
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