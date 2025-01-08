from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    soap_request = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/" xmlns:okt1="http://www.oktatas.hu">
      <soapenv:Header/>
      <soapenv:Body>
        <okt:Keres>
          <okt1:ApiKulcs>Hv-Tst-t312-r34q-v921-5318c</okt1:ApiKulcs>
          <okt1:Oktazon>76221103192</okt1:Oktazon>
        </okt:Keres>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    url = "https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc"
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://www.oktatas.hu/Keres"
    }

    response = requests.post(url, data=soap_request, headers=headers)

    if response.status_code == 200:
        return jsonify({
            "status": "success",
            "response": response.text
        })
    else:
        return jsonify({
            "status": "error",
            "code": response.status_code,
            "message": response.text
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
