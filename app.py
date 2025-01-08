from flask import Flask, jsonify, request
import requests
import urllib3
import xml.etree.ElementTree as ET
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

        # SOAP kérés XML dinamikus összeállítása
        namespaces = {
            'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
            'okt': 'http://www.oktatas.hu/',
            'okt1': 'http://www.oktatas.hu'
        }

        ET.register_namespace('soapenv', namespaces['soapenv'])
        ET.register_namespace('okt', namespaces['okt'])
        ET.register_namespace('okt1', namespaces['okt1'])

        envelope = ET.Element(ET.QName(namespaces['soapenv'], 'Envelope'))
        header = ET.SubElement(envelope, ET.QName(namespaces['soapenv'], 'Header'))
        body = ET.SubElement(envelope, ET.QName(namespaces['soapenv'], 'Body'))
        keres = ET.SubElement(body, ET.QName(namespaces['okt'], 'Keres'))
        
        # Paraméterek hozzáadása
        apikulcs = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'ApiKulcs'))
        apikulcs.text = 'Hv-Tst-t312-r34q-v921-5318c'
        
        azonosito = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'Azonosito'))
        azonosito.text = azon
        
        intezmeny_rovid_nev = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'IntezmenyRovidNev'))
        intezmeny_rovid_nev.text = 'KOSSUTH LAJOS ÁLTALÁNOS ISKOLA'
        
        intezmeny_telepules = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'IntezmenyTelepules'))
        intezmeny_telepules.text = 'GYÖNGYÖSPATA'
        
        jogosult_nev = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'JogosultNev'))
        
        elonev = ET.SubElement(jogosult_nev, ET.QName(namespaces['okt1'], 'Elonev'))
        elonev.text = ''
        
        keresztnev = ET.SubElement(jogosult_nev, ET.QName(namespaces['okt1'], 'Keresztnev'))
        keresztnev.text = 'Ádám'
        
        vezeteknev = ET.SubElement(jogosult_nev, ET.QName(namespaces['okt1'], 'Vezeteknev'))
        vezeteknev.text = 'Misuta'
        
        lakohely_telepules = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'LakohelyTelepules'))
        lakohely_telepules.text = 'GYÖNGYÖS'
        
        munkarend = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'Munkarend'))
        munkarend.text = 'NAPPALI'
        
        neme = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'Neme'))
        neme.text = 'F'
        
        oktazon = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'Oktazon'))
        oktazon.text = '76221103192'
        
        szuletesi_ev = ET.SubElement(keres, ET.QName(namespaces['okt1'], 'SzuletesiEv'))
        szuletesi_ev.text = '2010'

        # XML string előállítása
        soap_request = ET.tostring(envelope, encoding='utf-8', method='xml').decode('utf-8')

        # SOAP kérés küldése
        url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc'

        headers = {
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': 'http://www.oktatas.hu/IPublicServices/Keres',
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
