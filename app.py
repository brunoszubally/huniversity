from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check_student():
    # SOAP kérés tartalma
    soap_request = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:okt="http://www.oktatas.hu/" xmlns:okt1="http://www.oktatas.hu">
      <soapenv:Header/>
      <soapenv:Body>
        <okt:Keres>
          <okt1:ApiKulcs>TESZTsa</okt1:ApiKulcs>
          <okt1:Azonosito>1223433576</okt1:Azonosito>
          <okt1:IntezmenyRovidNev>KOSSUTH LAJOS ÁLTALÁNOS ISKOLA</okt1:IntezmenyRovidNev>
          <okt1:IntezmenyTelepules>GYÖNGYÖSPATA</okt1:IntezmenyTelepules>
          <okt1:JogosultNev>
            <okt1:Elonev/>
            <okt1:Keresztnev>Ádám</okt1:Keresztnev>
            <okt1:Vezeteknev>Misuta</okt1:Vezeteknev>
          </okt1:JogosultNev>
          <okt1:LakohelyTelepules>GYÖNGYÖS</okt1:LakohelyTelepules>
          <okt1:Munkarend>Nappali</okt1:Munkarend>
          <okt1:Neme>Ferfi</okt1:Neme>
          <okt1:Oktazon>76221103192</okt1:Oktazon>
          <okt1:SzuletesiEv>2010</okt1:SzuletesiEv>
        </okt:Keres>
      </soapenv:Body>
    </soapenv:Envelope>
    """

    # SOAP kérés küldése
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
