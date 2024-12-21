import urllib.parse
import requests
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

main_api = "https://www.mapquestapi.com/directions/v2/route?"
alternate_routes_api = "https://www.mapquestapi.com/directions/v2/alternateroutes?"
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
        settings["unit_system"] = unit_choice
        print(Fore.GREEN + "Updated successfully.\n")
    else:
        print(Fore.YELLOW + "No changes made.\n")

    vehicle_choice = input(Fore.WHITE + "Choose vehicle type (car/bike/foot): ").lower()
    if vehicle_choice in ["car", "bike", "foot"]:
        settings["vehicle_type"] = vehicle_choice
        print(Fore.GREEN + "Updated successfully.\n")
    else:
        print(Fore.YELLOW + "No changes made.\n")

    if settings["vehicle_type"] == "car":
        fuel_efficiency = input(Fore.WHITE + "Enter fuel efficiency: ")
        if fuel_efficiency.replace('.', '', 1).isdigit():
            settings["fuel_efficiency"] = float(fuel_efficiency)
            print(Fore.GREEN + "Updated successfully.\n")
        else:
            print(Fore.YELLOW + "No changes made.\n")
    else:
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

        destinations = []
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
        else:
            destinations.append(dest)

        add_more = input(Fore.WHITE + "\nWould you like to add more destinations? (Y/N): ").lower()
        if add_more == "y":
            print(Fore.CYAN + "\n- 'd' or 'done' to finish adding destinations.\n")
            while True:
                next_dest = input(Fore.WHITE + "Enter another destination: ")
                if next_dest.lower() in ["d", "done"]:
                    print(Fore.YELLOW + "Destination added.\n")
                    break
                elif next_dest.strip() == "":
                    print(Fore.RED + "Destination cannot be empty. Please enter a valid destination.\n")
                else:
                    destinations.append(next_dest)
                    print(Fore.YELLOW + "Destination added.\n")
        elif add_more == "n":
            pass

        mode_selection = {
            "car": "fastest",
            "bike": "bicycle",
            "foot": "pedestrian"
        }.get(settings["vehicle_type"], "fastest")

        unit_conversion = 1.60934 if settings["unit_system"] == "imperial" else 1

        main_query_params = [
            ("key", key),
            ("from", orig),
            ("to", destinations[0]),
            ("routeType", mode_selection),
            ("outFormat", "json")
        ]

        for dest in destinations[1:]:
            main_query_params.append(("to", dest))

        main_url = main_api + urllib.parse.urlencode(main_query_params, doseq=True)
        main_json_data = requests.get(main_url).json()
        main_json_status = main_json_data["info"]["statuscode"]

        if main_json_status == 0:
            print("\nAPI Status: " + Fore.GREEN + str(main_json_status) + ", Success!")
            print("URL: " + main_url)
            print(Fore.WHITE + "\n===============================================================")
            total_distance = 0
            total_fuel_used = 0
            multiple_destinations = len(destinations) > 1

            for leg_index, leg in enumerate(main_json_data["route"]["legs"]):
                if leg_index == 0:
                    print(Fore.WHITE + f"{orig} to {destinations[0]}:")
                else:
                    print(Fore.WHITE + f"{destinations[leg_index-1]} to {destinations[leg_index]}:")

                leg_distance = leg["distance"]
                total_distance += leg_distance

                if settings["unit_system"] == "imperial":
                    print("  • Distance: "+ Fore.YELLOW + f"{leg_distance:.2f}mi")
                else:
                    print("  • Distance: "+ Fore.YELLOW + f"{leg_distance * unit_conversion:.2f}km")

                print("  • Estimated Duration: " + Fore.YELLOW + f"{leg['formattedTime']}")

                if settings["vehicle_type"] == "car":
                    fuel_used = (leg_distance / (1.60934 if settings["unit_system"] == "imperial" else 1)) / settings["fuel_efficiency"]
                    total_fuel_used += fuel_used
                    fuel_unit = "G" if settings["unit_system"] == "imperial" else "L"
                    print("  • Fuel Used: " + Fore.YELLOW + f"{fuel_used:.2f}{fuel_unit}")

                print(Fore.WHITE + "\n  Turn-by-turn Directions:")
                for each in leg["maneuvers"]:
                    turn_distance = each["distance"] * (1.60934 if settings["unit_system"] == "imperial" else 1)
                    print(Fore.YELLOW + f"  ➔  {each['narrative']} ({turn_distance:.2f} {'mi' if settings['unit_system'] == 'imperial' else 'km'})")

            if multiple_destinations:
                print(Fore.WHITE + "\nTotal Distance Covered: " + Fore.YELLOW + f"{total_distance:.2f}{'mi' if settings['unit_system'] == 'imperial' else 'km'}")
                if settings["vehicle_type"] == "car":
                    print(Fore.WHITE + "Total Fuel Usage: " + Fore.YELLOW + f"{total_fuel_used:.2f}{'G' if settings['unit_system'] == 'imperial' else 'L'}")

            if len(destinations) == 1:
                max_routes = 4
                time_overage = 50
                alt_query_params = [
                    ("key", key),
                    ("from", orig),
                    ("to", destinations[0]),
                    ("maxRoutes", max_routes),
                    ("timeOverage", time_overage),
                    ("outFormat", "json")
                ]

                alt_url = alternate_routes_api + urllib.parse.urlencode(alt_query_params, doseq=True)
                alt_json_data = requests.get(alt_url).json()

                if "alternateRoutes" in alt_json_data["route"]:
                    for route_index, route in enumerate(alt_json_data["route"]["alternateRoutes"]):
                        print(Fore.CYAN + f"\nAlternate Route {route_index + 1}:")
                        total_distance = 0
                        total_fuel_used = 0

                        for leg_index, leg in enumerate(route["route"]["legs"]):
                            if leg_index == 0:
                                print(Fore.WHITE + f"{orig} to {destinations[0]}:")

                            leg_distance = leg["distance"]
                            total_distance += leg_distance

                            if settings["unit_system"] == "imperial":
                                print("  • Distance: "+ Fore.YELLOW + f"{leg_distance:.2f}mi")
                            else:
                                print("  • Distance: "+ Fore.YELLOW + f"{leg_distance * unit_conversion:.2f}km")

                            print("  • Estimated Duration: " + Fore.YELLOW + f"{leg['formattedTime']}")

                            if settings["vehicle_type"] == "car":
                                fuel_used = (leg_distance / (1.60934 if settings["unit_system"] == "imperial" else 1)) / settings["fuel_efficiency"]
                                total_fuel_used += fuel_used
                                fuel_unit = "G" if settings["unit_system"] == "imperial" else "L"
                                print("  • Fuel Used: " + Fore.YELLOW + f"{fuel_used:.2f}{fuel_unit}")

                            print(Fore.WHITE + "\n  Turn-by-turn Directions:")
                            for each in leg["maneuvers"]:
                                turn_distance = each["distance"] * (1.60934 if settings["unit_system"] == "imperial" else 1)
                                print(Fore.YELLOW + f"  ➔  {each['narrative']} ({turn_distance:.2f} {'mi' if settings['unit_system'] == 'imperial' else 'km'})")
                print(Fore.WHITE + "===============================================================")

        elif main_json_status == 402:
            print(Fore.RED + "Invalid input for one or more locations.")
        elif main_json_status == 611:
            print(Fore.RED + "Missing an entry for one or more locations.")
        else:
            print(Fore.RED + f"Status Code: {main_json_status}. Check the API documentation for details.")

try:
    main_loop()
except KeyboardInterrupt:
    print(Fore.RED + "\nProgram interrupted. Saving settings...")
    save_settings()
