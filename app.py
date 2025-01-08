from flask import Flask, jsonify
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check-student', methods=['GET', 'POST'])
def check_student():
    try:
        # SOAP kérés XML sablon
        soap_request = '''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/" xmlns:okt1="http://www.oktatas.hu">
            <soapenv:Header/>
            <soapenv:Body>
                <okt:Keres>
                    <okt1:ApiKulcs>Hv-Tst-t312-r34q-v921-5318c'</okt1:ApiKulcs>
                    <okt1:Azonosito>1223433576</okt1:Azonosito>
                    <okt1:IntezmenyRovidNev>KOSSUTH LAJOS ÁLTALÁNOS ISKOLA</okt1:IntezmenyRovidNev>
                    <okt1:IntezmenyTelepules>GYÖNGYÖSPATA</okt1:IntezmenyTelepules>
                    <okt1:JogosultNev>
                        <okt1:Elonev/>
                        <okt1:Keresztnev>Ádám</okt1:Keresztnev>
                        <okt1:Vezeteknev>Misuta</okt1:Vezeteknev>
                    </okt1:JogosultNev>
                    <okt1:LakohelyTelepules>GYÖNGYÖS</okt1:LakohelyTelepules>
                    <okt1:Munkarend>Nappali</okt1:Munkarend>
                    <okt1:Neme>Ferfi</okt1:Neme>
                    <okt1:Oktazon>76221103192</okt1:Oktazon>
                    <okt1:SzuletesiEv>2010</okt1:SzuletesiEv>
                </okt:Keres>
            </soapenv:Body>
        </soapenv:Envelope>
        '''

        # SOAP kérés küldése
        url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc'
        
        headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': 'http://www.oktatas.hu/Keres',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/xml, application/xml',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive'
        }

        print("Sending SOAP request...")
        response = requests.post(
            url=url,
            data=soap_request.encode('utf-8'),
            headers=headers,
            verify=False,
            timeout=30
        )
        print(f"Response status code: {response.status_code}")
        
        return jsonify({
            "status": "success",
            "http_status": response.status_code,
            "headers": dict(response.headers),
            "content_type": response.headers.get('content-type', ''),
            "response": response.text
        })

    except Exception as e:
        print(f"Error occurred: {str(e)}")
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