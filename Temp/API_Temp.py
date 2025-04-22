#imports
from datetime import datetime
import requests
import sqlite3
import json



def requestforTempAPI():
    ## API key initialization
    # met office api key
    met_api = "eyJ4NXQiOiJOak16WWpreVlUZGlZVGM0TUdSalpEaGtaV1psWWpjME5UTXhORFV4TlRZM1ptRTRZV1JrWWc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJDYW1lcm9uLnN0dWFydDExQHZpcmdpbm1lZGlhLmNvbUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6IkNhbWVyb24uc3R1YXJ0MTFAdmlyZ2lubWVkaWEuY29tIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJzaXRlX3NwZWNpZmljLWEzN2E2NWMyLWY1NGQtNDg2Zi1iODNkLTUxZmJmYjNiOGRhNSIsImlkIjo2Njc2LCJ1dWlkIjoiYWM0YWE4NmMtNzEyYS00NWE5LWJmODEtMmI2Njk4NDJhNTVhIn0sImlzcyI6Imh0dHBzOlwvXC9hcGktbWFuYWdlci5hcGktbWFuYWdlbWVudC5tZXRvZmZpY2UuY2xvdWQ6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsid2RoX3NpdGVfc3BlY2lmaWNfZnJlZSI6eyJ0aWVyUXVvdGFUeXBlIjoicmVxdWVzdENvdW50IiwiZ3JhcGhRTE1heENvbXBsZXhpdHkiOjAsImdyYXBoUUxNYXhEZXB0aCI6MCwic3RvcE9uUXVvdGFSZWFjaCI6dHJ1ZSwic3Bpa2VBcnJlc3RMaW1pdCI6MCwic3Bpa2VBcnJlc3RVbml0Ijoic2VjIn19LCJrZXl0eXBlIjoiUFJPRFVDVElPTiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IlNpdGVTcGVjaWZpY0ZvcmVjYXN0IiwiY29udGV4dCI6Ilwvc2l0ZXNwZWNpZmljXC92MCIsInB1Ymxpc2hlciI6IkphZ3Vhcl9DSSIsInZlcnNpb24iOiJ2MCIsInN1YnNjcmlwdGlvblRpZXIiOiJ3ZGhfc2l0ZV9zcGVjaWZpY19mcmVlIn1dLCJ0b2tlbl90eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzI4Mjk2MDAxLCJqdGkiOiI3ZDlmNDM4MS1iZmYwLTQ1ZTUtYTM0NS03MDZjNzUwMGZkZjYifQ==.Y5Pnrk9j6IbwRfFFyLyVZ-IDIcLcrED_McBP3aAiudDQ6ZScwOknOLNI8AxiZ8GlvJIehCUmjSomDN1-HV5TXQO3sKFTScwPtZzo6GmWrbsHBtiFvXNLDXzqYE4D_sbjcWKeM7Fcw5A3kaJ42XnQaZODufShW7cRbZ0KDWkQockcKVNMI5dTXSWFAP6do6DfdsZwXHaQ9eKhja4f-9QsLuQcX3beG0jrK-1gBWrys63bjfYekgkessIfwbC4usSVHbyrgOAybTLdzf-tMBTfe1x2FHKSjua0V03PMqauErXDle_-gbXuDszk2K8VS1G7omE449ICcHNWPeV2s2RAfw=="
    #geoapi
    geo_api = '0eac54586ab443299e4652cce0310a93'

    try:
        # Fetch postcode from the database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()

        cursor.execute("SELECT postcode FROM Temp_postcode ORDER BY id DESC LIMIT 1")  # Fetch the postcode with the highest ID
        postcode = cursor.fetchone()

        # If no postcode is found
        if postcode is None:
            print("No postcode found in the database.")
            return

        postcode = postcode[0]  # Extract the postcode from the tuple
        print(f"Retrieved Postcode: {postcode}")


        postcode_to_coordinates =  f"https://api.geoapify.com/v1/geocode/search?postcode={postcode}&apiKey={geo_api}"

        georesponse = requests.get(postcode_to_coordinates).json()

        latitude = georesponse['features'][0]['properties']['lat']
        longitude = georesponse['features'][0]['properties']['lon']

        print("printing courdinates",latitude,longitude)
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return
    
    try:
        met_office_url = f"https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly?latitude={latitude}&longitude={longitude}"

        headers = {
            'Content-Type': 'application/json',
            'Accept-Charset': 'UTF-8',
            'apikey': met_api
        }
        # call the API using the url and headers with the API key 
        response = requests.get(met_office_url, headers=headers)
        #saves into python dictorary and then converts it to a JSON string that can be stored into the database later 
        response_json = response.json()
        api_temp_json = json.dumps(response_json)

    except Exception as e:
        print(f"Error getting weather data: {e}")
        return
    
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Temp_api (apiTemp, "pub_date")
            VALUES (?, ?)
        ''', (api_temp_json, datetime.now()))

        # Commit the transaction
        conn.commit()
        # Close the connection
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

