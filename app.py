from flask import Flask, jsonify, request
import requests
import urllib3
from datetime import datetime
import xmltodict

# SSL figyelmeztetések letiltása
urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check-student', methods=['GET'])
def check_student():
    try:
        # Azonosító lekérése a query paraméterből
        azon = request.args.get('azonosito')
        if not azon:
            return jsonify({
                "status": "error",
                "message": "Az 'azonosito' paraméter kötelező."
            }), 400

        # Validáció: ellenőrizzük, hogy azonosító csak számokat tartalmaz-e
        if not azon.isdigit():
            return jsonify({
                "status": "error",
                "message": "Az 'azonosito' csak számokat tartalmazhat."
            }), 400

        # Előre definiált SOAP kérés XML sablon, az 'azon' változó beillesztése
        soap_request = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/" xmlns:okt1="http://www.oktatas.hu">
            <soapenv:Header/>
            <soapenv:Body>
                <okt:Keres>
                    <okt1:ApiKulcs>Hv-Tst-t312-r34q-v921-5318c</okt1:ApiKulcs>
                    <okt1:Azonosito>{azon}</okt1:Azonosito>
                </okt:Keres>
            </soapenv:Body>
        </soapenv:Envelope>
        '''

        # SOAP kérés küldése
        url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc'
        
        headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': '"http://www.oktatas.hu/IPublicServices/Keres"',  # Idézőjelek
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/xml, application/xml'
        }

        print("SOAP kérés küldése...")
        print(f"Kérés URL: {url}")
        print(f"Kérés fejléc: {headers}")
        print(f"Kérés törzse: {soap_request}")

        response = requests.post(
            url=url,
            data=soap_request.encode('utf-8'),
            headers=headers,
            verify=False,  # FIGYELEM: A verify=False használata biztonsági kockázattal jár
            timeout=30
        )

        print(f"Válasz státuszkód: {response.status_code}")
        print(f"Válasz fejléc: {dict(response.headers)}")
        print(f"Válasz törzse: {response.text}")

        if response.status_code == 200:
            # Válasz XML feldolgozása JSON formátumba
            response_dict = xmltodict.parse(response.content)
            return jsonify({
                "status": "success",
                "http_status": response.status_code,
                "headers": dict(response.headers),
                "content_type": response.headers.get('content-type', ''),
                "response": response_dict
            })
        else:
            return jsonify({
                "status": "error",
                "http_status": response.status_code,
                "headers": dict(response.headers),
                "content_type": response.headers.get('content-type', ''),
                "response": response.text
            }), response.status_code

    except Exception as e:
        print(f"Hiba történt: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e)),
            "details": str(getattr(e, 'detail', '')),
            "request": {
                "url": url,
                "headers": headers,
                "body": soap_request
            }
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
