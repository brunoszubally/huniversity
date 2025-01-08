from flask import Flask, jsonify, request
import requests
import urllib3
import xmltodict
from zeep import Client, Settings, Transport
from zeep.exceptions import Fault
from datetime import datetime

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

        # Zeep kliens beállítása
        wsdl = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        transport = Transport(timeout=30, verify=False)
        settings = Settings(strict=False, xml_huge_tree=True)
        client = Client(wsdl=wsdl, transport=transport, settings=settings)

        # SOAP művelet hívása
        response = client.service.Keres(
            ApiKulcs='Hv-Tst-t312-r34q-v921-5318c',
            Azonosito=azon,
            IntezmenyRovidNev='KOSSUTH LAJOS ÁLTALÁNOS ISKOLA',
            IntezmenyTelepules='GYÖNGYÖSPATA',
            JogosultNev={
                'Elonev': '',
                'Keresztnev': 'Ádám',
                'Vezeteknev': 'Misuta'
            },
            LakohelyTelepules='GYÖNGYÖS',
            Munkarend='NAPPALI',
            Neme='F',
            Oktazon='76221103192',
            SzuletesiEv=2010
        )

        # Válasz feldolgozása XML-ből JSON formátumba
        response_xml = client.wsdl.serialize_object(response)
        response_dict = xmltodict.parse(response_xml)

        return jsonify({
            "status": "success",
            "http_status": 200,
            "response": response_dict
        })

    except Fault as fault:
        print(f"Hiba történt: {fault}")
        return jsonify({
            "status": "error",
            "message": str(fault)
        }), 500
    except Exception as e:
        print(f"Hiba történt: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
