from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Hardware, API, Postcode
import pandas as pd
from datetime import datetime
import json
from .API_Temp import requestforTempAPI
from .Hardware import Get_Temp,Trigger_Solenoid
from apscheduler.schedulers.background import BackgroundScheduler


# Scheduler setup
scheduler = BackgroundScheduler()

# Schedule tasks
scheduler.add_job(Get_Temp, 'interval', minutes=10)
scheduler.add_job(requestforTempAPI, 'interval', days=1)

scheduler.start()
print("Scheduler started")

#requestforTempAPI()
#Get_Temp()
Trigger_Solenoid()

def index(request):
    # Fetch the latest 5 Hardware temperature records
    temp_list = Hardware.objects.order_by("-pub_date")[:5]

    # Attempt to get the latest API data
    try:
        queryset = API.objects.latest('pub_date')
        # Convert the queryset to a DataFrame
        df = pd.DataFrame.from_records([queryset.__dict__])
        # Parse the JSON string in apiTemp column
        json_data = df['apiTemp'][0]  # If it's already a dictionary, this will be fine.
        if isinstance(json_data, str):
            json_data = json.loads(json_data)  # Deserialize if it's a string
        
        time_series = json_data['features'][0]['properties']['timeSeries']
        # Filter out unnecessary columns
        mylist = [
            'screenDewPointTemperature', 'windSpeed10m', 'windDirectionFrom10m',
            'windGustSpeed10m', 'max10mWindGust', 'visibility', 'screenRelativeHumidity',
            'mslp', 'uvIndex', 'significantWeatherCode', 'precipitationRate',
            'totalPrecipAmount', 'totalSnowAmount', 'probOfPrecipitation'
        ]
        filtered_df = pd.DataFrame(time_series).drop(columns=mylist)

        # Convert filtered DataFrame to a dictionary
        API_List = filtered_df.to_dict(orient='records')

        # Converting 'time' field to datetime
        for api in API_List:
            if isinstance(api['time'], str):
                api['time'] = datetime.strptime(api['time'], "%Y-%m-%dT%H:%MZ")  # Convert from string to datetime
            elif isinstance(api['time'], datetime):
                pass  # If it's already a datetime object, leave it as is

        today = datetime.today().date()

        # Filter API data for today's date
        API_List = [api for api in API_List if api['time'].date() == today]

    except API.DoesNotExist:
        # If no API data exists in the database
        print("No API data found in the database.")
        API_List = []

    # Prepare the context to pass to the template

    context = {
        "temp_list": temp_list,
        "API_List": API_List,
    }

    # Render the template with the context
    return render(request, "Temp/index.html", context)
    
def submit_postcode(request):
    if request.method == 'POST':
        # Get the postcode value from the form
        postcode_value = request.POST.get('postcode')

        # Check if the postcode already exists in the database
        try:
            postcode = Postcode.objects.get(id=1)  
            postcode.postcode = postcode_value 
            postcode.save()  
        except Postcode.DoesNotExist:
            # If no Postcode exists, create a new one
            Postcode.objects.create(postcode=postcode_value)

        # Redirect index page
        return redirect('index')
    else:
        # returns back to submit_postcode if it fails
        return render(request, 'Temp/submit_postcode.html')
