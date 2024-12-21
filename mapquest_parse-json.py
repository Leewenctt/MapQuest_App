import urllib.parse
import requests

main_api = "https://www.mapquestapi.com/directions/v2/route?"
key = "AJ83WSCLuL4L2EXPUfYkpoxIfAxZlTFV"
fuel_efficiency = 12

while True:
    orig = input("Starting Location: ")
    if orig.lower() in ["quit", "q"]:
        break

    dest = input("Destination: ")
    if dest.lower() in ["quit", "q"]:
        break

    mode = input("Choose vehicle type (Car, Bike, Foot): ").lower()
    mode_selection = {"car": "fastest", "bike": "bicycle", "foot": "pedestrian"}.get(mode, "fastest")

    url = main_api + urllib.parse.urlencode({"key": key, "from": orig, "to": dest, "routeType": mode_selection})

    json_data = requests.get(url).json()
    json_status = json_data["info"]["statuscode"]

    if json_status == 0:
        print("\nAPI Status: " + str(json_status) + " = A successful route call.")
        print("URL: " + url)
        print("\n===============================================================")
        print("Directions from " + orig + " to " + dest + " by " + mode + ":")
        distance_km = json_data["route"]["distance"] * 1.61
        print("  • Distance: " + str("{:.2f}".format(json_data["route"]["distance"])) + "mi / " + str("{:.2f}".format(distance_km)) + "km")
        print("  • Estimated Trip Duration: " + json_data["route"]["formattedTime"])
        
        if mode_selection == "fastest":
            fuel_used = distance_km / fuel_efficiency
            print("  • Estimated Fuel Usage (L): " + str("{:.2f}".format(fuel_used)))
        
        print("\nTurn-by-turn Directions:")
        for each in json_data["route"]["legs"][0]["maneuvers"]:
            print("  ➢  " + each["narrative"] + " (" + str("{:.2f}".format(each["distance"] * 1.61)) + " km)")
        print("===============================================================\n")

    elif json_status == 402: 
        print("*************************************************************")
        print("Status Code: " + str(json_status) + "; Invalid user inputs for one or both locations.")
        print("**********************************************\n")

    elif json_status == 611:
        print("*************************************************************")
        print("Status Code: " + str(json_status) + "; Missing an entry for one or both locations.")
        print("**********************************************\n")

    else:
        print("************************************************************************")
        print("For Status Code: " + str(json_status) + "; Refer to:")
        print("https://developer.mapquest.com/documentation/directions-api/status-codes")
        print("************************************************************************\n")
