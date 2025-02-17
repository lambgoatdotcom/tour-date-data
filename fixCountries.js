const fs = require('fs');

// US state abbreviations
const usStates = new Set([
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]);

// Mapping for non-US abbreviations (add more mappings as needed)
const countryMapping = {
    "VN": "Vietnam",
    "HK": "Hong Kong"
};

// Load and process the JSON data
const filePath = 'tour_data_processed.json';
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

data.forEach(event => {
    if (usStates.has(event.state)) {
        // It's a US state – force to United States
        event.country = "United States";
    } else if (countryMapping[event.state]) {
        // Known international mapping provided
        event.country = countryMapping[event.state];
    } else {
        // Fallback: if not found, assume the state code is the country code
        event.country = event.state;
    }
});

fs.writeFileSync(filePath, JSON.stringify(data, null, 4), 'utf8');
console.log("Tour data country fields have been updated."); 