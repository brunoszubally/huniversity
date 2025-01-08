from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    soap_request = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
      <soapenv:Header/>
      <soapenv:Body>
        <tem:Ellenoriz>
          <tem:apiKulcs>Hv-Tst-t312-r34q-v921-5318c</tem:apiKulcs>
          <tem:oktatasiAzonosito>76221103192</tem:oktatasiAzonosito>
        </tem:Ellenoriz>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    url = "https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc"
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tempuri.org/IPublicServices/Ellenoriz"
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
