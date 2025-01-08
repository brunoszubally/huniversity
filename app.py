from flask import Flask, jsonify
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    # Részletesebb hibaüzenetek engedélyezése
    settings = Settings(strict=False, xml_huge_tree=True)
    
    # Session létrehozása speciális fejlécekkel
    session = Session()
    session.verify = False  # SSL ellenőrzés kikapcsolása (csak teszteléshez!)
    transport = Transport(session=session)
    
    # WSDL kliens létrehozása
    wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/SingleWsdl'
    client = Client(wsdl_url, transport=transport, settings=settings)
    
    try:
        # Service és port információk kiírása debug célból
        print("Available services:", [service.name for service in client.wsdl.services.values()])
        print("Available operations:", [operation.name for operation in client.wsdl.services[0].ports[0].binding._operations.values()])
        
        # Szolgáltatás hívása
        service = client.create_service(
            "{http://tempuri.org/}BasicHttpBinding_IPublicServices",
            "https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc"
        )
        
        result = service.Ellenoriz(
            apiKulcs='Hv-Tst-t312-r34q-v921-5318c',
            oktatasiAzonosito='76221103192'
        )
        
        return jsonify({
            "status": "success",
            "response": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "details": str(type(e))
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
