
def Trigger_Solenoid():

    # Set the pin numbering mode (BCM or BOARD)
    GPIO.setmode(GPIO.BCM) 

    # Set up GPIO pin 17 as an output
    GPIO.setup(17, GPIO.OUT)

    try:
        # Turn on GPIO pin 17
        GPIO.output(17, GPIO.HIGH)
        print("GPIO 17 is ON")
        
        time.sleep(20)
        print("20 seconds")
        time.sleep(20)
        
        # Turn off GPIO pin 17
        GPIO.output(17, GPIO.LOW)
        print("GPIO 17 is OFF")

    finally:
        # Clean up GPIO settings
        GPIO.cleanup()
        print("GPIO cleanup complete")




def Get_Temp():
    SERVICE_UUID = "ebe0ccb0-7a0a-4b0c-8a1a-6ff2997da3a6"
    CHARACTERISTIC_UUID = "ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6"

    result = {}

    async def read_temperature(client):
        try:
            print(f"Attempting to read from: {CHARACTERISTIC_UUID}")
            data = await client.read_gatt_char(CHARACTERISTIC_UUID)
            temp = (data[0] | (data[1] << 8)) * 0.01
            result['temp'] = temp
            print(f"Temp = {temp:.1f} C")
        except Exception as e:
            print(f"Failed to read temperature: {e}")

    async def connect_and_read(address):
        try:
            async with BleakClient(address, timeout=20.0) as client:
                if client.is_connected:
                    print(f"Connected to {address}")
                    await read_temperature(client)
        except Exception as e:
            print(f"Error while connecting/reading: {e}")

    async def scan_and_connect():
        devices = await BleakScanner.discover()
        for device in devices:
            print(f"Found: {device.name} [{device.address}]")
            if device.name == "LYWSD03MMC":
                print(f"Found target device: {device.address}")
                await connect_and_read(device.address)
                break
        else:
            print("Target device not found.")

    asyncio.run(scan_and_connect())

    # Insert into DB if a reading was successfully obtained
    if 'temp' in result:
        try:
            temp_value = float(result['temp'])
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Temp_hardware (hardTemp, "pub_date")
                VALUES (?, ?)
            ''', (temp_value, datetime.now()))

            conn.commit()
            conn.close()
            print("Temperature inserted into DB.")
        except Exception as e:
            print(f"Database error: {e}")
    else:
        print("No temperature reading available.")



def check_temperature():
    try:
        # Get the latest hardware temperature
        latest_temp = Hardware.objects.latest('pub_date')
        current_time = timezone.now()

        # Check if temperature is at risk of freezing and trigger the solinoid if so
        if latest_temp.hardTemp <= 0:
            print("Warning: The temperature is <= 0°C!")
            Trigger_Solenoid()

        # Check if data is failing to update 
        time_diff = current_time - latest_temp.pub_date
        if time_diff > timedelta(hours=1):
            print("Warning: It has been over an hour since the last temperature update!")

            # Try to use the latest API data as fallback plan
            try:
                latest_api = API.objects.latest('pub_date')
                api_data = json.loads(latest_api.apiTemp) if isinstance(latest_api.apiTemp, str) else latest_api.apiTemp

                # Get current hour in UTC and match API's format
                current_hour = timezone.now().astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
                current_hour_str = current_hour.isoformat().replace('+00:00', 'Z')

                time_series = api_data['features'][0]['properties']['timeSeries']
                match = next((entry for entry in time_series if entry['time'] == current_hour_str), None)

                if match:
                    screen_temp = match.get('screenTemperature')
                    print(f"Fallback API temperature at {current_hour_str}: {screen_temp}°C")
                    # Optional: Trigger solenoid based on fallback temperature
                    if screen_temp <= 0:
                        print("Warning (API): Fallback temperature is <= 0°C!")
                        Trigger_Solenoid()
                else:
                    print(f"No matching API temperature found for {current_hour_str}")
            except API.DoesNotExist:
                print("No API data available for fallback.")
            except Exception as e:
                print(f"Error while handling API fallback: {e}")
        else:
            print(f"Temperature is fine: {latest_temp.hardTemp}°C")
            print(f"Last updated: {latest_temp.pub_date}")

    except Hardware.DoesNotExist:
        print("No hardware temperature data available.")

