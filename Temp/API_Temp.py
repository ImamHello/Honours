#imports
from datetime import datetime
import requests
import sqlite3
#import geojson
import json



def requestforTempAPI():
    ## API key initialization
    # met office api key
    met_api = "eyJ4NXQiOiJOak16WWpreVlUZGlZVGM0TUdSalpEaGtaV1psWWpjME5UTXhORFV4TlRZM1ptRTRZV1JrWWc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJDYW1lcm9uLnN0dWFydDExQHZpcmdpbm1lZGlhLmNvbUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6IkNhbWVyb24uc3R1YXJ0MTFAdmlyZ2lubWVkaWEuY29tIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJzaXRlX3NwZWNpZmljLWEzN2E2NWMyLWY1NGQtNDg2Zi1iODNkLTUxZmJmYjNiOGRhNSIsImlkIjo2Njc2LCJ1dWlkIjoiYWM0YWE4NmMtNzEyYS00NWE5LWJmODEtMmI2Njk4NDJhNTVhIn0sImlzcyI6Imh0dHBzOlwvXC9hcGktbWFuYWdlci5hcGktbWFuYWdlbWVudC5tZXRvZmZpY2UuY2xvdWQ6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsid2RoX3NpdGVfc3BlY2lmaWNfZnJlZSI6eyJ0aWVyUXVvdGFUeXBlIjoicmVxdWVzdENvdW50IiwiZ3JhcGhRTE1heENvbXBsZXhpdHkiOjAsImdyYXBoUUxNYXhEZXB0aCI6MCwic3RvcE9uUXVvdGFSZWFjaCI6dHJ1ZSwic3Bpa2VBcnJlc3RMaW1pdCI6MCwic3Bpa2VBcnJlc3RVbml0Ijoic2VjIn19LCJrZXl0eXBlIjoiUFJPRFVDVElPTiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IlNpdGVTcGVjaWZpY0ZvcmVjYXN0IiwiY29udGV4dCI6Ilwvc2l0ZXNwZWNpZmljXC92MCIsInB1Ymxpc2hlciI6IkphZ3Vhcl9DSSIsInZlcnNpb24iOiJ2MCIsInN1YnNjcmlwdGlvblRpZXIiOiJ3ZGhfc2l0ZV9zcGVjaWZpY19mcmVlIn1dLCJ0b2tlbl90eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzI4Mjk2MDAxLCJqdGkiOiI3ZDlmNDM4MS1iZmYwLTQ1ZTUtYTM0NS03MDZjNzUwMGZkZjYifQ==.Y5Pnrk9j6IbwRfFFyLyVZ-IDIcLcrED_McBP3aAiudDQ6ZScwOknOLNI8AxiZ8GlvJIehCUmjSomDN1-HV5TXQO3sKFTScwPtZzo6GmWrbsHBtiFvXNLDXzqYE4D_sbjcWKeM7Fcw5A3kaJ42XnQaZODufShW7cRbZ0KDWkQockcKVNMI5dTXSWFAP6do6DfdsZwXHaQ9eKhja4f-9QsLuQcX3beG0jrK-1gBWrys63bjfYekgkessIfwbC4usSVHbyrgOAybTLdzf-tMBTfe1x2FHKSjua0V03PMqauErXDle_-gbXuDszk2K8VS1G7omE449ICcHNWPeV2s2RAfw=="
    #geoapi
    geo_api = '0eac54586ab443299e4652cce0310a93'


    postcode = "G4 OBA"

    postcode_to_coordinates =  f"https://api.geoapify.com/v1/geocode/search?postcode={postcode}&apiKey={geo_api}"

    georesponse = requests.get(postcode_to_coordinates)
    georesponse = georesponse.json()

    latitude = georesponse['features'][0]['properties']['lat']
    longitude = georesponse['features'][0]['properties']['lon']

    print(latitude,longitude)

    met_office_url = f"https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly?latitude={latitude}&longitude={longitude}"

    headers = {
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8',
        'apikey': met_api
    }
    # Make the GET request
    response = requests.get(met_office_url, headers=headers)
    #Print the JSON response it gets 2 days worth of data from 3 hours before the call seemingly
    response_json = response.json()
    api_temp_json = json.dumps(response_json)
    print(api_temp_json)


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



# so here is where i think i have everything i need 


    # import json
    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(response.json(), f, ensure_ascii=False, indent=4)



    # import pandas as pd
    # from datetime import datetime


    # with open("/content/data.json") as f:
    #     data = json.load(f)

    # df = pd.DataFrame(data)
    # print(df)
    # pd.set_option('expand_frame_repr', False)
    # json_column = df['features'][0]['properties']['timeSeries']
    # json_column = pd.DataFrame(json_column)
    # mylist=['screenDewPointTemperature','windSpeed10m','windDirectionFrom10m','windGustSpeed10m','max10mWindGust','visibility','screenRelativeHumidity','mslp','uvIndex','significantWeatherCode','precipitationRate','totalPrecipAmount','totalSnowAmount','probOfPrecipitation']
    # filterd=json_column.drop(columns = mylist)
    # print(filterd)

    # filterd['time'] = pd.to_datetime(filterd['time'], format='ISO8601')

    # # Filter data between two dates
    # filtered_df = df.loc[(filterd['time'] >= '2024-10-17')
    #                     & (filterd['time'] < '2024-10-18')]

    # filtered_df=json_column.drop(columns = mylist)
    # filtered_df[filtered_df['time'] < '2024-10-18']
    # print(filtered_df[filtered_df['time'] < '2024-10-18'])


    # print(filtered_df[(filtered_df['time'] > '2024-10-18') & (filtered_df['time'] <= '2024-10-19')])