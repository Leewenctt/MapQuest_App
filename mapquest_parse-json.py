import urllib.parse
import requests
import json
import os

main_api = "https://www.mapquestapi.com/directions/v2/route?"
key = "AJ83WSCLuL4L2EXPUfYkpoxIfAxZlTFV"

script_dir = os.path.dirname(os.path.abspath(__file__))
settings_file = os.path.join(script_dir, "settings.json")

default_settings = {
    "unit_system": "metric",
    "vehicle_type": "car",
    "fuel_efficiency": 12
}

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            return json.load(file)
    else:
        return default_settings

def save_settings():
    with open(settings_file, 'w') as file:
        json.dump(settings, file, indent=4)

settings = load_settings()

def update_settings():
    print("\n===============================================================")
    print(f"Current settings:\n  • Unit System: {settings['unit_system']}\n  • Vehicle Type: {settings['vehicle_type']}\n  • Fuel Efficiency: {settings['fuel_efficiency']} \n")

    unit_choice = input("Choose unit system (metric/imperial): ").lower()
    if unit_choice in ["metric", "imperial"]:
        print("Updated successfully.\n")
        settings["unit_system"] = unit_choice
    else:
        print("No changes made.\n")

    vehicle_choice = input(f"Choose vehicle type (car/bike/foot): ").lower()
    if vehicle_choice in ["car", "bike", "foot"]:
        print("Updated successfully.\n")
        settings["vehicle_type"] = vehicle_choice
    else:
        print("No changes made.\n")
        
    fuel_efficiency = input(f"Enter fuel efficiency (for 'car' only): ")
    if fuel_efficiency.replace('.', '', 1).isdigit():
        print("Updated successfully.\n")
        settings["fuel_efficiency"] = float(fuel_efficiency)
    else:
        print("No changes made.\n")

    save_settings()
    print("===============================================================")

def main_loop():
    while True:
        print("\n- 's' or 'settings' to update settings.")
        print("- 'q' or 'quit' to quit.\n")

        orig = input("Starting Location: ")
        if orig.lower() in ["quit", "q"]:
            print("Thank you for using our app.")
            break
        elif orig.lower() in ["settings", "s"]:
            update_settings()
            continue
        elif orig.strip() == "":
            print("Starting location cannot be empty. Please enter a valid starting location.\n")
            continue

        dest = input("Destination: ")
        if dest.lower() in ["quit", "q"]:
            print("Thank you for using our app.")
            break
        elif dest.lower() in ["settings", "s"]:
            update_settings()
            continue
        elif dest.strip() == "":
            print("Destination cannot be empty. Please enter a valid destination.\n")
            continue

        vehicle_choice = input(f"Choose vehicle type (Car/Bike/Foot): ").lower()
        if vehicle_choice in ["car", "bike", "foot"]:
            settings["vehicle_type"] = vehicle_choice
        elif vehicle_choice.strip() == "":
            print("No vehicle type selected, using default.")
            vehicle_choice = settings["vehicle_type"]

        mode = vehicle_choice.lower()
        mode_selection = {"car": "fastest", "bike": "bicycle", "foot": "pedestrian"}.get(mode, "fastest")

        unit_conversion = 1.60934 if settings["unit_system"] == "imperial" else 1

        url = main_api + urllib.parse.urlencode({"key": key, "from": orig, "to": dest, "routeType": mode_selection})

        json_data = requests.get(url).json()
        json_status = json_data["info"]["statuscode"]

        if json_status == 0:
            print("\nAPI Status: " + str(json_status) + " = A successful route call.")
            print("URL: " + url)
            print("\n===============================================================")
            print("Directions from " + orig + " to " + dest + " by " + mode + ":")
            
            distance = json_data["route"]["distance"]
            if settings["unit_system"] == "imperial":
                print(f"  • Distance: {distance:.2f}mi")
                print(f"  • Estimated Trip Duration: {json_data['route']['formattedTime']}")
                fuel_used = (distance / 1.60934) / settings["fuel_efficiency"]
                print(f"  • Estimated Fuel Usage: {fuel_used:.2f}G")
            else:
                distance_km = distance * 1.60934
                print(f"  • Distance: {distance_km:.2f}km")
                print(f"  • Estimated Trip Duration: {json_data['route']['formattedTime']}")
                fuel_used = (distance_km * unit_conversion) / settings["fuel_efficiency"]
                print(f"  • Estimated Fuel Usage: {fuel_used:.2f}L")

            print("\nTurn-by-turn Directions:")
            for each in json_data["route"]["legs"][0]["maneuvers"]:
                turn_distance = each["distance"] * (1.60934 if settings["unit_system"] == "imperial" else 1)
                if settings["unit_system"] == "imperial":
                    print(f"  ➢  {each['narrative']} ({turn_distance:.2f} mi)")
                else:
                    print(f"  ➢  {each['narrative']} ({turn_distance:.2f} km)")

            print("===============================================================")

        elif json_status == 402:
            print("\n*************************************************************")
            print("Status Code: " + str(json_status) + "; Invalid user inputs for one or both locations.")
            print("*************************************************************\n")

        elif json_status == 611:
            print("\n*************************************************************")
            print("Status Code: " + str(json_status) + "; Missing an entry for one or both locations.")
            print("*************************************************************\n")

        else:
            print("\n************************************************************************")
            print("For Status Code: " + str(json_status) + "; Refer to:")
            print("https://developer.mapquest.com/documentation/directions-api/status-codes")
            print("************************************************************************\n")

if __name__ == "__main__":
    main_loop()