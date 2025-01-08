import requests
import urllib3
urllib3.disable_warnings()

def get_wsdl():
    url = 'https://ws.oh.gov.hu/oktig-kartyaelfogado-test/?SingleWsdl'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/xml,application/xml',
        'Cache-Control': 'no-cache'
    }
    
    try:
        print(f"Fetching WSDL from: {url}")
        response = requests.get(
            url, 
            headers=headers,
            verify=False,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            with open('service.wsdl', 'wb') as f:
                f.write(response.content)
            print("WSDL saved to service.wsdl")
            return True
        else:
            print(f"Failed to fetch WSDL: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    get_wsdl() 