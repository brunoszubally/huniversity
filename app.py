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
        service_details = {
            "services": [],
            "operations": [],
            "bindings": [],
            "types": []
        }
        
        # Szolgáltatások és műveletek listázása
        for service in client.wsdl.services.values():
            service_details["services"].append(service.name)
            
            for port in service.ports.values():
                for operation in port.binding._operations.values():
                    service_details["operations"].append({
                        "service": service.name,
                        "port": port.name,
                        "operation": operation.name,
                        "input": str(operation.input.signature()) if hasattr(operation.input, 'signature') else str(operation.input),
                        "output": str(operation.output.signature()) if hasattr(operation.output, 'signature') else str(operation.output)
                    })

        # Binding-ok listázása
        for binding in client.wsdl.bindings.values():
            service_details["bindings"].append(str(binding))

        # Típusok listázása (ha vannak)
        if client.wsdl.types:
            for type_obj in client.wsdl.types.types:
                service_details["types"].append(str(type_obj))

        return jsonify({
            "status": "success",
            "service_details": service_details
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
