from flask import Flask, jsonify
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
import urllib3

urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        session = Session()
        session.verify = False
        session.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'text/xml;charset=UTF-8'
        }
        
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        client = Client(wsdl_url, transport=Transport(session=session))

        # Szolgáltatás részleteinek kigyűjtése
        service_info = {}
        
        # Szolgáltatások listázása
        for service in client.wsdl.services.values():
            service_info[service.name] = {
                "ports": {}
            }
            
            # Portok listázása
            for port in service.ports.values():
                service_info[service.name]["ports"][port.name] = {
                    "operations": []
                }
                
                # Műveletek listázása
                for operation in port.binding._operations.values():
                    service_info[service.name]["ports"][port.name]["operations"].append({
                        "name": operation.name,
                        "input": str(operation.input),
                        "output": str(operation.output)
                    })

        return jsonify({
            "status": "success",
            "service_info": service_info,
            "bindings": list(client.wsdl.bindings.keys()),
            "messages": list(client.wsdl.messages.keys()),
            "types": list(client.wsdl.types.types.keys()) if client.wsdl.types else []
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e)),
            "details": str(getattr(e, 'detail', ''))
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
