import json

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
}

# Load the processed tour data
with open('tour_data_processed.json', 'r') as f:
    tours = json.load(f)

# Iterate through each tour and its tour_dates list
for tour in tours:
    for date in tour.get("tour_dates", []):
        state = date.get("state", "").strip()
        if state in US_STATES:
            date["country"] = "United States"

# Write back the updated data
with open('tour_data_processed.json', 'w') as f:
    json.dump(tours, f, indent=4) 