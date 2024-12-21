import urllib.parse
import requests
import json
import os
from colorama import Fore, Style, init

# Initialize Colorama for colored terminal output
init(autoreset=True)

# Define the main MapQuest API endpoint and the alternate routes API
main_api = "https://www.mapquestapi.com/directions/v2/route?"
alternate_routes_api = "https://www.mapquestapi.com/directions/v2/alternateroutes?"
key = "AJ83WSCLuL4L2EXPUfYkpoxIfAxZlTFV"  # API key for MapQuest

# Get the directory of the script to save the settings file
script_dir = os.path.dirname(os.path.abspath(__file__))
settings_file = os.path.join(script_dir, "settings.json")

# Default settings for unit system, vehicle type, and fuel efficiency
default_settings = {
    "unit_system": "metric",  # Default unit system is metric
    "vehicle_type": "car",    # Default vehicle type is car
    "fuel_efficiency": 12     # Default fuel efficiency for car (km per liter)
}

# Function to load settings from a JSON file
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            return json.load(file)  # Load settings if the file exists
    else:
        return default_settings  # Return default settings if file doesn't exist

# Function to save updated settings to a JSON file
def save_settings():
    with open(settings_file, 'w') as file:
        json.dump(settings, file, indent=4)  # Save the settings in pretty JSON format

# Load current settings at the start of the program
settings = load_settings()

# Function to update settings interactively
def update_settings():
    print(Fore.WHITE + "\n===============================================================")
    print(f"Current settings:\n  • Unit System: {settings['unit_system']}\n  • Vehicle Type: {settings['vehicle_type']}\n  • Fuel Efficiency: {settings['fuel_efficiency']} \n")

    # Update unit system choice (metric or imperial)
    while True:
        unit_choice = input(Fore.WHITE + "Choose unit system (metric/imperial): ").lower()
        if unit_choice in ["metric", "imperial"]:
            settings["unit_system"] = unit_choice
            print(Fore.GREEN + "Updated successfully.\n")
            break
        else:
            print(Fore.YELLOW + "Invalid input. Please enter 'metric' or 'imperial'.")

    # Update vehicle type choice (car, bike, foot)
    while True:
        vehicle_choice = input(Fore.WHITE + "Choose vehicle type (car/bike/foot): ").lower()
        if vehicle_choice in ["car", "bike", "foot"]:
            settings["vehicle_type"] = vehicle_choice
            print(Fore.GREEN + "Updated successfully.\n")
            break
        else:
            print(Fore.YELLOW + "Invalid input. Please enter 'car', 'bike', or 'foot'.\n")

    # Update fuel efficiency if vehicle type is car
    if settings["vehicle_type"] == "car":
        while True:
            fuel_efficiency = input(Fore.WHITE + "Enter fuel efficiency: ")
            if fuel_efficiency.replace('.', '', 1).isdigit():
                settings["fuel_efficiency"] = float(fuel_efficiency)
                print(Fore.GREEN + "Updated successfully.\n")
                break
            else:
                print(Fore.YELLOW + "Invalid input. Please enter a valid number for fuel efficiency.\n")
    else:
        print(Fore.YELLOW + "Fuel efficiency is not applicable for this vehicle type.\n")

    # Save the updated settings to the file
    save_settings()
    print(Fore.WHITE + "===============================================================")

# Function to handle API error responses
def handle_api_error(main_json_data):
    if "info" in main_json_data and "statuscode" in main_json_data["info"]:
        status_code = main_json_data["info"]["statuscode"]
        print(Fore.RED + f"API Error {status_code}: {main_json_data['info']['messages'][0]}")
    else:
        print(Fore.RED + "Error: Missing or unexpected API response.")

# Main loop to interact with the user
def main_loop():
    global settings
    while True:
        try:
            # Display options for settings or quitting
            print(Fore.CYAN + "\n- 's' or 'settings' to update settings.")
            print(Fore.CYAN + "- 'q' or 'quit' to quit.\n")

            # Ask for starting location
            orig = input(Fore.WHITE + "Starting Location: ")
            if orig.lower() in ["quit", "q"]:
                print(Fore.GREEN + "Thank you for using our app.")
                break
            elif orig.lower() in ["settings", "s"]:
                update_settings()  # Update settings if chosen
                settings = load_settings()  # Reload settings after update
                continue
            elif orig.strip() == "":
                print(Fore.RED + "Starting location cannot be empty. Please enter a valid starting location.\n")
                continue

            # Ask for destination(s)
            destinations = []
            dest = input(Fore.WHITE + "Destination: ")
            if dest.lower() in ["quit", "q"]:
                print(Fore.GREEN + "Thank you for using our app.")
                break
            elif dest.lower() in ["settings", "s"]:
                update_settings()  # Update settings if chosen
                settings = load_settings()  # Reload settings after update
                continue
            elif dest.strip() == "":
                print(Fore.RED + "Destination cannot be empty. Please enter a valid destination.\n")
                continue
            else:
                destinations.append(dest)

            # Ask if user wants to add more destinations
            while True:
                add_more = input(Fore.WHITE + "\nWould you like to add more destinations? (Y/N): ").lower()
                if add_more == "y":
                    print(Fore.CYAN + "\n- 'd' or 'done' to finish adding destinations.\n")
                    while True:
                        next_dest = input(Fore.WHITE + "Enter another destination: ")
                        if next_dest.lower() in ["d", "done"]:
                            break
                        elif next_dest.strip() == "":
                            print(Fore.RED + "Destination cannot be empty. Please enter a valid destination.\n")
                        else:
                            destinations.append(next_dest)
                            print(Fore.YELLOW + "Destination added.\n")
                    break
                elif add_more == "n":
                    break
                else:
                    print(Fore.RED + "Invalid input. Please enter 'Y' or 'N'.")

            # Option to optimize the route order
            if len(destinations) > 1:
                while True:
                    optimize_choice = input(Fore.WHITE + "\nWould you like to optimize the route order for efficiency? (Y/N): ").lower()
                    if optimize_choice in ['y', 'n']:
                        break
                    else:
                        print(Fore.RED + "Invalid input. Please enter 'Y' or 'N'.\n")
                api_endpoint = "https://www.mapquestapi.com/directions/v2/optimizedroute?" if optimize_choice == 'y' else main_api
            else:
                api_endpoint = main_api
                optimize_choice = 'n'

            # Option to enable alternate routes for a single destination
            alternate_choice = 'n'
            if len(destinations) == 1:
                while True:
                    alternate_choice = input(Fore.WHITE + "\nEnable alternate routes? (Y/N): ").lower()
                    if alternate_choice in ['y', 'n']:
                        break
                    else:
                        print(Fore.RED + "Invalid input. Please enter 'Y' or 'N'.")

            # Set the mode of travel based on the user's settings
            mode_selection = {
                "car": "fastest",  # Car uses 'fastest' route
                "bike": "bicycle",  # Bike uses 'bicycle' route
                "foot": "pedestrian"  # Foot uses 'pedestrian' route
            }.get(settings["vehicle_type"], "fastest")  # Default to fastest if no valid vehicle type

            # Set conversion factor for distance based on unit system
            unit_conversion = 1.60934 if settings["unit_system"] == "imperial" else 1

            # Build API query parameters
            if optimize_choice == 'y':
                locations = [orig] + destinations
                locations_json = {"locations": locations}
                main_query_params = [
                    ("key", key),
                    ("json", json.dumps(locations_json)),
                    ("outFormat", "json")
                ]
            else:
                main_query_params = [
                    ("key", key),
                    ("from", orig),
                    ("to", destinations[0]),
                    ("routeType", mode_selection),
                    ("outFormat", "json")
                ]
                for dest in destinations[1:]:
                    main_query_params.append(("to", dest))

            # Generate the URL for the main API request
            main_url = api_endpoint + urllib.parse.urlencode(main_query_params, doseq=True)

            try:
                # Send the request to the MapQuest API
                response = requests.get(main_url)
                main_json_data = response.json()
                main_json_status = main_json_data["info"]["statuscode"]

                if main_json_status == 0:
                    print("\nAPI Status: " + Fore.GREEN + str(main_json_status) + ", Success!")
                    print("URL: " + main_url)
                    print(Fore.WHITE + "\n===============================================================")

                    # Display the optimized or standard route
                    if optimize_choice == 'y':
                        print(Fore.CYAN + "Optimized Route:")
                    else:
                        print(Fore.CYAN + "Standard Route:")

                    total_distance = 0
                    total_fuel_used = 0

                    # If optimized route, print the optimized stop order
                    if optimize_choice == 'y' and "locationSequence" in main_json_data["route"]:
                        location_sequence = main_json_data["route"]["locationSequence"]
                        print(Fore.YELLOW + "\nOptimized Stop Order:")
                        all_locations = [orig] + destinations
                        
                        if all(isinstance(idx, int) and 0 <= idx < len(all_locations) for idx in location_sequence):
                            for i, idx in enumerate(location_sequence, 2):
                                print(f"{i-1}. {all_locations[idx]}")
                            print()
                        else:
                            print(Fore.RED + "Warning: Received invalid location sequence from API")
                            print(f"1. {orig} (Start)")
                            for i, dest in enumerate(destinations, 2):
                                print(f"{i}. {dest}")
                            print()

                    # Print the route details (legs, distance, time, fuel usage)
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

                        # Calculate and print fuel usage for car
                        if settings["vehicle_type"] == "car":
                            fuel_used = (leg_distance / (1.60934 if settings["unit_system"] == "imperial" else 1)) / settings["fuel_efficiency"]
                            total_fuel_used += fuel_used
                            fuel_unit = "G" if settings["unit_system"] == "imperial" else "L"
                            print("  • Fuel Used: " + Fore.YELLOW + f"{fuel_used:.2f}{fuel_unit}")

                        # Print turn-by-turn directions
                        print(Fore.WHITE + "\n  Turn-by-turn Directions:")
                        for each in leg["maneuvers"]:
                            turn_distance = each["distance"] * unit_conversion
                            print(Fore.YELLOW + f"  ➔  {each['narrative']} ({turn_distance:.2f} {'mi' if settings['unit_system'] == 'imperial' else 'km'})")
                            
                        if len(destinations) > 1:
                            print()

                    # Print total distance and fuel used (if applicable)
                    if len(destinations) > 1:
                        print(Fore.WHITE + "\nTotal Distance Covered: " + Fore.YELLOW + f"{total_distance * unit_conversion:.2f}{'mi' if settings['unit_system'] == 'imperial' else 'km'}")
                        if settings["vehicle_type"] == "car":
                            print(Fore.WHITE + "Total Fuel Usage: " + Fore.YELLOW + f"{total_fuel_used:.2f}{'G' if settings['unit_system'] == 'imperial' else 'L'}")

                    # If alternate routes were enabled, fetch and display alternate routes
                    if alternate_choice == 'y' and len(destinations) == 1:
                        max_routes = 2
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
                        try:
                            alt_json_data = requests.get(alt_url).json()

                            if "alternateRoutes" in alt_json_data["route"]:
                                for route_index, route in enumerate(alt_json_data["route"]["alternateRoutes"]):
                                    print(Fore.CYAN + f"\nAlternate Route:")
                                    total_distance = 0
                                    total_fuel_used = 0

                                    for leg_index, leg in enumerate(route["route"]["legs"]):
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
                                    for leg_index, leg in enumerate(route["route"]["legs"]):
                                        for each in leg["maneuvers"]:
                                            turn_distance = each["distance"] * unit_conversion
                                            print(Fore.YELLOW + f"  ➔  {each['narrative']} ({turn_distance:.2f} {'mi' if settings['unit_system'] == 'imperial' else 'km'})")

                                    print(Fore.WHITE + "\nTotal Distance Covered: " + Fore.YELLOW + f"{total_distance * unit_conversion:.2f}{'mi' if settings['unit_system'] == 'imperial' else 'km'}")
                                    if settings["vehicle_type"] == "car":
                                        print(Fore.WHITE + "Total Fuel Usage: " + Fore.YELLOW + f"{total_fuel_used:.2f}{'G' if settings['unit_system'] == 'imperial' else 'L'}")
                        except Exception as e:
                            print(Fore.RED + f"Error fetching alternate routes: {str(e)}")
                else:
                    handle_api_error(main_json_data)

            except Exception as e:
                print(Fore.RED + f"Error fetching route data: {str(e)}")
        except Exception as e:
            print(Fore.RED + f"An unexpected error occurred: {str(e)}")

# Start the main loop
main_loop()
