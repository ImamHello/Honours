import RPi.GPIO as GPIO
import time
import asyncio
from bleak import BleakClient, BleakScanner



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


import asyncio
import sqlite3
from datetime import datetime
from bleak import BleakClient, BleakScanner

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
