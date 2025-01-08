import requests

url = "https://ws.oh.gov.hu/oktig-kartyaelfogado-test/publicservices.svc"
soap_action = "http://www.oktatas.hu/IOktigKartyaelfogadoPublicService/Keres"

xml_body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                               xmlns:okt="http://www.oktatas.hu/" 
                               xmlns:okt1="http://www.oktatas.hu">
   <soapenv:Header/>
   <soapenv:Body>
      <okt:Keres>
         <okt1:ApiKulcs>Hv-Tst-t312-r34q-v921-5318c</okt1:ApiKulcs>
         <okt1:Azonosito>1223433576</okt1:Azonosito>
         <!-- ... További opcionális mezők, ha szeretnéd ... -->
      </okt:Keres>
   </soapenv:Body>
</soapenv:Envelope>
"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": soap_action
}

resp = requests.post(url, data=xml_body.encode("utf-8"), headers=headers)

print(resp.status_code)
print(resp.text)
