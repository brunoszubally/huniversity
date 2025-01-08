from flask import Flask, jsonify
from zeep import Client
from zeep.transports import Transport
from requests import Session

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    try:
        session = Session()
        session.verify = False
        
        wsdl_url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
        client = Client(
            wsdl_url,
            transport=Transport(session=session)
        )

        # Szolgáltatások listázása
        available_operations = []
        for service in client.wsdl.services.values():
            print(f"\nService: {service.name}")
            available_operations.append(f"Service: {service.name}")
            
            for port in service.ports.values():
                print(f"Port: {port.name}")
                available_operations.append(f"Port: {port.name}")
                
                operations = port.binding._operations.values()
                for operation in operations:
                    print(f"Operation: {operation.name}")
                    available_operations.append(f"Operation: {operation.name}")
        
        return jsonify({
            "status": "success",
            "available_operations": available_operations
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": str(type(e))
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
