from django.shortcuts import render
from django.http import HttpResponse
from .models import Hardware, API
import pandas as pd
from datetime import datetime
from .API_Temp import requestforTempAPI

# Convert the queryset to a DataFrame
queryset = API.objects.latest('pub_date')
df = pd.DataFrame.from_records([queryset.__dict__])
# Access JSON data
json_data = df['apiTemp'][0]  # Access the first row's JSON data
time_series = json_data['features'][0]['properties']['timeSeries']
time_series_df = pd.DataFrame(time_series)

# Filtering
mylist = [
    'screenDewPointTemperature', 'windSpeed10m', 'windDirectionFrom10m',
    'windGustSpeed10m', 'max10mWindGust', 'visibility', 'screenRelativeHumidity',
    'mslp', 'uvIndex', 'significantWeatherCode', 'precipitationRate',
    'totalPrecipAmount', 'totalSnowAmount', 'probOfPrecipitation'
]
filtered_df = time_series_df.drop(columns=mylist)

from apscheduler.schedulers.background import BackgroundScheduler


def some_job():
    print ("Decorated job",datetime.now())

scheduler = BackgroundScheduler()
scheduler.add_job(some_job, 'interval', hours=1)
scheduler.start()
print("wow")
print("Decorated job",datetime.now())


#requestforTempAPI()

def index(request):
    # Fetch latest 5 Hardware temps
    temp_list = Hardware.objects.order_by("-pub_date")[:5]

    # Convert the filtered DataFrame to a dictionary
    API_List = filtered_df.to_dict(orient='records')

    # Converting 'time' field to a datetime 
    for api in API_List:
        api['time'] = datetime.strptime(api['time'], "%Y-%m-%dT%H:%MZ")

    for api in API_List:
            if isinstance(api['time'], str):
                api['time'] = datetime.strptime(api['time'], "%Y-%m-%dT%H:%MZ")  # Convert from string to datetime
            elif isinstance(api['time'], datetime):
                api['time'] = api['time']  # If it's already a datetime object, leave it as is
    today = datetime.today().date()

    API_List = [api for api in API_List if api['time'].date() == today]

    context = {
        "temp_list": temp_list,
        "API_List": API_List,
    }
    return render(request, "Temp/index.html", context)