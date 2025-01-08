from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# SOAP konfiguráció
API_URL = "https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc"  # Teszt környezet URL-je
SOAP_ACTION = "http://www.oktatas.hu/IOktigKartyaelfogadoPublicService/Keres"  # SOAP Action
API_KEY = "TESZT"  # Teszt API kulcs (valós környezetben cseréld le az éles kulcsra)

@app.route("/ellenoriz", methods=["POST"])
def ellenoriz_diak():
    """
    Diákigazolvány ellenőrzése SOAP segítségével.
    """
    # Kérés JSON body kinyerése
    data = request.get_json()

    if not data or "Azonosito" not in data:
        return jsonify({"error": "A 'Azonosito' mező kötelező"}), 400

    # SOAP XML kérés összeállítása
    azonosito = data["Azonosito"]
    nev = data.get("JogosultNev", {})
    keresztnev = nev.get("Keresztnev", "")
    vezeteknev = nev.get("Vezeteknev", "")
    szuletesi_ev = data.get("SzuletesiEv", "")
    neme = data.get("Neme", "")
    munkarend = data.get("Munkarend", "")
    intezmeny_rovid_nev = data.get("IntezmenyRovidNev", "")
    intezmeny_telepules = data.get("IntezmenyTelepules", "")
    lakohely_telepules = data.get("LakohelyTelepules", "")

    # SOAP XML kérést készítünk
    soap_request = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                                       xmlns:okt="http://www.oktatas.hu/" 
                                       xmlns:okt1="http://www.oktatas.hu">
        <soapenv:Header/>
        <soapenv:Body>
            <okt:Keres>
                <okt1:ApiKulcs>{API_KEY}</okt1:ApiKulcs>
                <okt1:Azonosito>{azonosito}</okt1:Azonosito>
                <okt1:JogosultNev>
                    <okt1:Elonev></okt1:Elonev>
                    <okt1:Keresztnev>{keresztnev}</okt1:Keresztnev>
                    <okt1:Vezeteknev>{vezeteknev}</okt1:Vezeteknev>
                </okt1:JogosultNev>
                <okt1:SzuletesiEv>{szuletesi_ev}</okt1:SzuletesiEv>
                <okt1:Neme>{neme}</okt1:Neme>
                <okt1:Munkarend>{munkarend}</okt1:Munkarend>
                <okt1:IntezmenyRovidNev>{intezmeny_rovid_nev}</okt1:IntezmenyRovidNev>
                <okt1:IntezmenyTelepules>{intezmeny_telepules}</okt1:IntezmenyTelepules>
                <okt1:LakohelyTelepules>{lakohely_telepules}</okt1:LakohelyTelepules>
            </okt:Keres>
        </soapenv:Body>
    </soapenv:Envelope>"""

    # SOAP kérés küldése
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": SOAP_ACTION
    }

    try:
        response = requests.post(API_URL, data=soap_request.encode("utf-8"), headers=headers)
        response.raise_for_status()  # Hibák ellenőrzése

        # SOAP válasz visszaadása JSON-ként
        return jsonify({"response": response.text}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # A Flask szerver futtatása (IP-t és portot állíts be, ha szükséges)
    app.run(host="0.0.0.0", port=5000, debug=True)
