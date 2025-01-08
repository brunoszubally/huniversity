from flask import Flask, jsonify
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check-student', methods=['GET', 'POST'])
def check_student():
    try:
        # SOAP kérés XML sablon a dokumentáció alapján
        soap_request = '''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/" xmlns:okt1="http://www.oktatas.hu">
            <soapenv:Header/>
            <soapenv:Body>
                <okt:Keres>
                    <okt1:ApiKulcs>TESZT</okt1:ApiKulcs>
                    <okt1:Azonosito>1210000825</okt1:Azonosito>
                    <okt1:IntezmenyRovidNev>Balassi Bálint Gimnázium</okt1:IntezmenyRovidNev>
                    <okt1:IntezmenyTelepules>Eger</okt1:IntezmenyTelepules>
                    <okt1:JogosultNev>
                        <okt1:Elonev/>
                        <okt1:Keresztnev>Eszmerálda</okt1:Keresztnev>
                        <okt1:Vezeteknev>Koncsíta</okt1:Vezeteknev>
                    </okt1:JogosultNev>
                    <okt1:LakohelyTelepules>Nagykanizsa</okt1:LakohelyTelepules>
                    <okt1:Munkarend>NAPPALI</okt1:Munkarend>
                    <okt1:Neme>N</okt1:Neme>
                    <okt1:Oktazon>459632</okt1:Oktazon>
                    <okt1:SzuletesiEv>2004</okt1:SzuletesiEv>
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
            'Accept': 'text/xml, application/xml'
        }

        print("Sending SOAP request...")
        print(f"Request URL: {url}")
        print(f"Request headers: {headers}")
        print(f"Request body: {soap_request}")
        
        response = requests.post(
            url=url,
            data=soap_request.encode('utf-8'),
            headers=headers,
            verify=False,
            timeout=30
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
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