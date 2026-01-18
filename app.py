from flask import Flask, jsonify, request
import requests
import urllib3
import os
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

@app.route('/ip-test', methods=['GET'])
def ip_test():
    try:
        proxy_url = os.environ.get("QUOTAGUARDSTATIC_URL")

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        r = requests.get("https://ip.quotaguard.com", proxies=proxies, timeout=20)
        return jsonify({
            "status": "success",
            "ip": r.text.strip()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/check-student', methods=['GET'])
def check_student():
    try:
        azonosito = request.args.get('azonosito')

        if not azonosito:
            return jsonify({
                "status": "error",
                "message": "Az 'azonosito' paraméter megadása kötelező"
            }), 400

        if len(azonosito) != 10 or not (azonosito.startswith('0') or azonosito.startswith('1')):
            return jsonify({
                "status": "error",
                "code": 4,
                "message": "Érvénytelen azonosító formátum"
            }), 400

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

        url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-live/publicservices.svc'

        headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': 'http://www.oktatas.hu/IPublicServices/DiakigazolvanyJogosultsagLekerdezes',
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/xml, application/xml'
        }

        proxy_url = os.environ.get("QUOTAGUARDSTATIC_URL")

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        response = requests.post(
            url=url,
            data=soap_request.encode('utf-8'),
            headers=headers,
            proxies=proxies,
            verify=False,
            timeout=30
        )

        if 'KedvezmenyreJogosult' in response.text:
            return jsonify({"status": "success", "code": 1})
        elif 'KedvezmenyreNemJogosult' in response.text:
            return jsonify({"status": "success", "code": 2})
        elif 'NemLetezoKartya' in response.text:
            return jsonify({"status": "success", "code": 3})
        else:
            return jsonify({
                "status": "error",
                "code": 0,
                "message": "Ismeretlen válasz"
            })

    except Exception as e:
        return jsonify({
            "status": "error",
            "code": 0,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
