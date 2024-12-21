import urllib.parse
import requests
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

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
    print(Fore.WHITE + "\n===============================================================")
    print(f"Current settings:\n  • Unit System: {settings['unit_system']}\n  • Vehicle Type: {settings['vehicle_type']}\n  • Fuel Efficiency: {settings['fuel_efficiency']} \n")

    unit_choice = input(Fore.WHITE + "Choose unit system (metric/imperial): ").lower()
    if unit_choice in ["metric", "imperial"]:
        print(Fore.GREEN + "Updated successfully.\n")
        settings["unit_system"] = unit_choice
    else:
        print(Fore.YELLOW + "No changes made.\n")

    vehicle_choice = input(Fore.WHITE + "Choose vehicle type (car/bike/foot): ").lower()
    if vehicle_choice in ["car", "bike", "foot"]:
        print(Fore.GREEN + "Updated successfully.\n")
        settings["vehicle_type"] = vehicle_choice
    else:
        print(Fore.YELLOW + "No changes made.\n")

    if settings["vehicle_type"] == "car":
        fuel_efficiency = input(Fore.WHITE + "Enter fuel efficiency: ")
        if fuel_efficiency.replace('.', '', 1).isdigit():
            print(Fore.GREEN + "Updated successfully.\n")
            settings["fuel_efficiency"] = float(fuel_efficiency)
        else:
            print(Fore.YELLOW + "No changes made.\n")
    else:
        print(Fore.WHITE + "Enter fuel efficiency: ")
        print(Fore.YELLOW + "Fuel efficiency is not applicable for this vehicle type.\n")

    save_settings()
    print(Fore.WHITE + "===============================================================")

def main_loop():
    while True:
        print(Fore.CYAN + "\n- 's' or 'settings' to update settings.")
        print(Fore.CYAN + "- 'q' or 'quit' to quit.\n")

        orig = input(Fore.WHITE + "Starting Location: ")
        if orig.lower() in ["quit", "q"]:
            print(Fore.GREEN + "Thank you for using our app.")
            break
        elif orig.lower() in ["settings", "s"]:
            update_settings()
            continue
        elif orig.strip() == "":
            print(Fore.RED + "Starting location cannot be empty. Please enter a valid starting location.\n")
            continue

        dest = input(Fore.WHITE + "Destination: ")
        if dest.lower() in ["quit", "q"]:
            print(Fore.GREEN + "Thank you for using our app.")
            break
        elif dest.lower() in ["settings", "s"]:
            update_settings()
            continue
        elif dest.strip() == "":
            print(Fore.RED + "Destination cannot be empty. Please enter a valid destination.\n")
            continue

        vehicle_choice = input(Fore.WHITE + f"Choose vehicle type (Car/Bike/Foot): ").lower()
        if vehicle_choice in ["car", "bike", "foot"]:
            settings["vehicle_type"] = vehicle_choice
        elif vehicle_choice.strip() == "":
            print(Fore.YELLOW + "No vehicle type selected, using default.")
            vehicle_choice = settings["vehicle_type"]

        mode = vehicle_choice.lower()
        mode_selection = {"car": "fastest", "bike": "bicycle", "foot": "pedestrian"}.get(mode, "fastest")

        unit_conversion = 1.60934 if settings["unit_system"] == "imperial" else 1

        url = main_api + urllib.parse.urlencode({"key": key, "from": orig, "to": dest, "routeType": mode_selection})

        json_data = requests.get(url).json()
        json_status = json_data["info"]["statuscode"]

        if json_status == 0:
            print("\nAPI Status: " + Fore.GREEN + str(json_status) + ", Success!")
            print("URL: " + url)
            print(Fore.WHITE + "\n===============================================================")
            print("Directions from " + Fore.YELLOW + orig + Fore.WHITE + " to " + Fore.YELLOW + dest + Fore.WHITE + " by " + Fore.YELLOW + mode + Fore.WHITE + ":")

            distance = json_data["route"]["distance"]
            if settings["unit_system"] == "imperial":
                print(Fore.YELLOW + f"  • Distance: {distance:.2f}mi")
                print(Fore.YELLOW + f"  • Estimated Trip Duration: {json_data['route']['formattedTime']}")
                fuel_used = (distance / 1.60934) / settings["fuel_efficiency"]
                print(Fore.YELLOW + f"  • Estimated Fuel Usage: {fuel_used:.2f}G")
            else:
                distance_km = distance * 1.60934
                print(Fore.YELLOW + f"  • Distance: {distance_km:.2f}km")
                print(Fore.YELLOW + f"  • Estimated Trip Duration: {json_data['route']['formattedTime']}")
                fuel_used = (distance_km * unit_conversion) / settings["fuel_efficiency"]
                print(Fore.YELLOW + f"  • Estimated Fuel Usage: {fuel_used:.2f}L")

            print(Fore.WHITE + "\nTurn-by-turn Directions:")
            for each in json_data["route"]["legs"][0]["maneuvers"]:
                turn_distance = each["distance"] * (1.60934 if settings["unit_system"] == "imperial" else 1)
                if settings["unit_system"] == "imperial":
                    print(Fore.YELLOW + f"  ➔  {each['narrative']} ({turn_distance:.2f} mi)")
                else:
                    print(Fore.YELLOW + f"  ➔  {each['narrative']} ({turn_distance:.2f} km)")

            print(Fore.WHITE + "===============================================================")

        elif json_status == 402:
            print(Fore.RED + "\n*************************************************************")
            print("Status Code: " + str(json_status) + "; Invalid user inputs for one or both locations.")
            print("*************************************************************\n")

        elif json_status == 611:
            print(Fore.RED + "\n*************************************************************")
            print("Status Code: " + str(json_status) + "; Missing an entry for one or both locations.")
            print("*************************************************************\n")

        else:
            print(Fore.RED + "\n************************************************************************")
            print("For Status Code: " + str(json_status) + "; Refer to:")
            print("https://developer.mapquest.com/documentation/directions-api/status-codes")
            print("************************************************************************\n")

try:
    main_loop()
except KeyboardInterrupt:
    print(Fore.RED + "\nProgram interrupted. Saving settings...")
    save_settings()