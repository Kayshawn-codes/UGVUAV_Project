from gpsdclient import GPSDClient

try:
    # Connect to gpsd, typically running on localhost:2947
    # Use with statement for automatic client closure
    with GPSDClient(host="127.0.0.1") as client:
        # Iterate through the stream of GPS reports as dictionaries
        # Filter for 'TPV' messages which contain primary location data
        print("Client")
        for result in client.dict_stream(convert_datetime=True, filter=["TPV"]):
            print("Loop")
            # Extract and print relevant data if available
            latitude = result.get("lat", "n/a")
            longitude = result.get("lon", "n/a")
            time = result.get("time", "n/a")
            mode = result.get("mode", "n/a") # 0=Invalid, 1=NO_FIX, 2=2D, 3=3D

            print(f"Time: {time}")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
            print(f"Fix Mode: {mode} ({['Invalid', 'NO_FIX', '2D', '3D'][mode if isinstance(mode, int) and 0 <= mode <= 3 else 0]})")
            print("-" * 30)

except ConnectionRefusedError:
    print("Error: Could not connect to gpsd. Ensure gpsd is running.")
except KeyboardInterrupt:
    print("\nClient stopped by user.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
