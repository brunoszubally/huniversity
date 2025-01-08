from flask import Flask, jsonify
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check-student', methods=['GET', 'POST'])
def check_student():
    try:
        # SOAP kérés XML sablon a helyes művelettel
        soap_request = '''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/">
            <soapenv:Header/>
            <soapenv:Body>
                <okt:DiakigazolvanyJogosultsagLekerdezes>
                    <okt:ApiKulcs>TESZT</okt:ApiKulcs>
                    <okt:Azonosito>1223433576</okt:Azonosito>
                    <okt:IntezmenyRovidNev>KOSSUTH LAJOS ÁLTALÁNOS ISKOLA</okt:IntezmenyRovidNev>
                    <okt:IntezmenyTelepules>GYÖNGYÖSPATA</okt:IntezmenyTelepules>
                    <okt:JogosultNev>
                        <okt:Elonev/>
                        <okt:Keresztnev>Ádám</okt:Keresztnev>
                        <okt:Vezeteknev>Misuta</okt:Vezeteknev>
                    </okt:JogosultNev>
                    <okt:LakohelyTelepules>GYÖNGYÖS</okt:LakohelyTelepules>
                    <okt:Munkarend>Nappali</okt:Munkarend>
                    <okt:Neme>Ferfi</okt:Neme>
                    <okt:Oktazon>76221103192</okt:Oktazon>
                    <okt:SzuletesiEv>2010</okt:SzuletesiEv>
                </okt:DiakigazolvanyJogosultsagLekerdezes>
            </soapenv:Body>
        </soapenv:Envelope>
        '''

        # SOAP kérés küldése
        url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc'
        
        headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': 'http://www.oktatas.hu/DiakigazolvanyJogosultsagLekerdezes',
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