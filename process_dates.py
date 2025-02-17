import json
import re
import unicodedata
from datetime import datetime
from bs4 import BeautifulSoup

# Global country mapping
COUNTRY_MAPPING = {
    'AF': 'Afghanistan',
    'AL': 'Albania',
    'DZ': 'Algeria',
    'AD': 'Andorra',
    'AO': 'Angola',
    'AG': 'Antigua and Barbuda',
    'AR': 'Argentina',
    'AM': 'Armenia',
    'AU': 'Australia',
    'AT': 'Austria',
    'AZ': 'Azerbaijan',
    'BS': 'Bahamas',
    'BH': 'Bahrain',
    'BD': 'Bangladesh',
    'BB': 'Barbados',
    'BY': 'Belarus',
    'BE': 'Belgium',
    'BZ': 'Belize',
    'BJ': 'Benin',
    'BT': 'Bhutan',
    'BO': 'Bolivia',
    'BA': 'Bosnia and Herzegovina',
    'BW': 'Botswana',
    'BR': 'Brazil',
    'BN': 'Brunei',
    'BG': 'Bulgaria',
    'BF': 'Burkina Faso',
    'BI': 'Burundi',
    'KH': 'Cambodia',
    'CM': 'Cameroon',
    'CA': 'Canada',
    'CV': 'Cape Verde',
    'CF': 'Central African Republic',
    'TD': 'Chad',
    'CL': 'Chile',
    'CN': 'China',
    'CO': 'Colombia',
    'KM': 'Comoros',
    'CG': 'Congo (Brazzaville)',
    'CD': 'Congo (Kinshasa)',
    'CR': 'Costa Rica',
    'CI': "Côte d'Ivoire",
    'HR': 'Croatia',
    'CU': 'Cuba',
    'CY': 'Cyprus',
    'CZ': 'Czech Republic',
    'DK': 'Denmark',
    'DJ': 'Djibouti',
    'DM': 'Dominica',
    'DO': 'Dominican Republic',
    'EC': 'Ecuador',
    'EG': 'Egypt',
    'SV': 'El Salvador',
    'GQ': 'Equatorial Guinea',
    'ER': 'Eritrea',
    'EE': 'Estonia',
    'SZ': 'Eswatini',
    'ET': 'Ethiopia',
    'FJ': 'Fiji',
    'FI': 'Finland',
    'FR': 'France',
    'GA': 'Gabon',
    'GM': 'Gambia',
    'GE': 'Georgia',
    'DE': 'Germany',
    'GH': 'Ghana',
    'GR': 'Greece',
    'GD': 'Grenada',
    'GT': 'Guatemala',
    'GN': 'Guinea',
    'GW': 'Guinea-Bissau',
    'GY': 'Guyana',
    'HT': 'Haiti',
    'HN': 'Honduras',
    'HU': 'Hungary',
    'IS': 'Iceland',
    'IN': 'India',
    'ID': 'Indonesia',
    'IR': 'Iran',
    'IQ': 'Iraq',
    'IE': 'Ireland',
    'IL': 'Israel',
    'IT': 'Italy',
    'JM': 'Jamaica',
    'JP': 'Japan',
    'JO': 'Jordan',
    'KZ': 'Kazakhstan',
    'KE': 'Kenya',
    'KI': 'Kiribati',
    'KP': 'North Korea',
    'KR': 'South Korea',
    'KW': 'Kuwait',
    'KG': 'Kyrgyzstan',
    'LA': 'Laos',
    'LV': 'Latvia',
    'LB': 'Lebanon',
    'LS': 'Lesotho',
    'LR': 'Liberia',
    'LY': 'Libya',
    'LI': 'Liechtenstein',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MG': 'Madagascar',
    'MW': 'Malawi',
    'MY': 'Malaysia',
    'MV': 'Maldives',
    'ML': 'Mali',
    'MT': 'Malta',
    'MH': 'Marshall Islands',
    'MR': 'Mauritania',
    'MU': 'Mauritius',
    'MX': 'Mexico',
    'FM': 'Micronesia',
    'MD': 'Moldova',
    'MC': 'Monaco',
    'MN': 'Mongolia',
    'ME': 'Montenegro',
    'MA': 'Morocco',
    'MZ': 'Mozambique',
    'MM': 'Myanmar',
    'NA': 'Namibia',
    'NR': 'Nauru',
    'NP': 'Nepal',
    'NL': 'Netherlands',
    'NZ': 'New Zealand',
    'NI': 'Nicaragua',
    'NE': 'Niger',
    'NG': 'Nigeria',
    'NO': 'Norway',
    'OM': 'Oman',
    'PK': 'Pakistan',
    'PW': 'Palau',
    'PA': 'Panama',
    'PG': 'Papua New Guinea',
    'PY': 'Paraguay',
    'PE': 'Peru',
    'PH': 'Philippines',
    'PL': 'Poland',
    'PT': 'Portugal',
    'QA': 'Qatar',
    'RO': 'Romania',
    'RU': 'Russia',
    'RW': 'Rwanda',
    'KN': 'Saint Kitts and Nevis',
    'LC': 'Saint Lucia',
    'VC': 'Saint Vincent and the Grenadines',
    'WS': 'Samoa',
    'SM': 'San Marino',
    'ST': 'Sao Tome and Principe',
    'SA': 'Saudi Arabia',
    'SN': 'Senegal',
    'RS': 'Serbia',
    'SC': 'Seychelles',
    'SL': 'Sierra Leone',
    'SG': 'Singapore',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'SB': 'Solomon Islands',
    'SO': 'Somalia',
    'ZA': 'South Africa',
    'ES': 'Spain',
    'LK': 'Sri Lanka',
    'SD': 'Sudan',
    'SR': 'Suriname',
    'SE': 'Sweden',
    'CH': 'Switzerland',
    'SY': 'Syria',
    'TW': 'Taiwan',
    'TJ': 'Tajikistan',
    'TZ': 'Tanzania',
    'TH': 'Thailand',
    'TL': 'Timor-Leste',
    'TG': 'Togo',
    'TO': 'Tonga',
    'TT': 'Trinidad and Tobago',
    'TN': 'Tunisia',
    'TR': 'Turkey',
    'TM': 'Turkmenistan',
    'UG': 'Uganda',
    'UA': 'Ukraine',
    'UK': 'United Kingdom',
    'AE': 'United Arab Emirates',
    'GB': 'United Kingdom',
    'US': 'United States',
    'UY': 'Uruguay',
    'UZ': 'Uzbekistan',
    'VU': 'Vanuatu',
    'VA': 'Vatican City',
    'VE': 'Venezuela',
    'VN': 'Vietnam',
    'YE': 'Yemen',
    'ZM': 'Zambia',
    'ZW': 'Zimbabwe',
    'HK': 'Hong Kong',
    'MO': 'Macau',
    'XK': 'Kosovo',
    # Canadian provinces/territories mapped to Canada
    'ON': 'Canada',
    'QC': 'Canada',
    'BC': 'Canada',
    'AB': 'Canada',
    'MB': 'Canada',
    'SK': 'Canada',
    'NS': 'Canada',
    'NB': 'Canada',
    'NL': 'Canada',
    'PE': 'Canada',
    'YT': 'Canada',
    'NT': 'Canada',
    'NU': 'Canada'
}

# Precompiled regex patterns for date extraction and testing
EXTRACT_PATTERNS = [
    re.compile(r'(\d{1,2})[/.-](\d{1,2})(?:[/.-]\d{2,4})?\s+([\w\s.-]+?),\s*([A-Z]{2})\s*(?:@@|@|at|-)\s*([^@\n]+)\s*(?:–|\u2013|to)?\s*([^@\n]*)'),
    re.compile(r'(\d{1,2})[/.-](\d{1,2})(?:[/.-]\d{2,4})?\s+([\w\s.-]+?)\s*(?:@@|@|at|-)\s*([^@\n]+)\s*(?:–|\u2013|to)?\s*([^@\n]*)'),
    re.compile(r'(\d{1,2})[/.-](\d{1,2})(?:[/.-]\d{2,4})?\s+([^@\n]+)\s*(?:–|\u2013|to)?\s*([^@\n]*)')
]

TEST_PATTERNS = [
    re.compile(r'(\d{1,2})[/.-](\d{1,2})(?:[/.-](?:\d{2}|\d{4}))?\s+([\w\s.-]+),\s*([A-Z]{2})\s*(?:@@|@|at|-)\s*(.*?)(?=\d{1,2}[/.-]|$)\s*(?:–|\u2013|to)?\s*(.*?)(?=\d{1,2}[/.-]|$)'),
    re.compile(r'(\d{1,2})[/.-](\d{1,2})(?:[/.-](?:\d{2}|\d{4}))?\s+([\w\s.-]+)\s*(?:@@|@|at|-)\s*(.*?)(?=\d{1,2}[/.-]|$)\s*(?:–|\u2013|to)?\s*(.*?)(?=\d{1,2}[/.-]|$)'),
    re.compile(r'(\d{1,2})[/.-](\d{1,2})(?:[/.-](?:\d{2}|\d{4}))?\s+(.*?)(?=\d{1,2}[/.-]|$)\s*(?:–|\u2013|to)?\s*(.*?)(?=\d{1,2}[/.-]|$)')
]

# Add these definitions after your imports
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
}

CANADIAN_PROVINCES = {
    'ON', 'QC', 'BC', 'AB', 'MB', 'SK', 'NS', 'NB', 'NL', 'PE', 'YT', 'NT', 'NU'
}

def clean_line(line):
    """Clean a line of text by removing extra whitespace, HTML entities, and unwanted annotations."""
    line = line.strip()
    line = re.sub(r'\s+', ' ', line)
    line = re.sub(r'&nbsp;', ' ', line)
    line = re.sub(r'(?i)dates?:?\s*', '', line)
    line = re.sub(r'(?i)tour\s+dates?:?\s*', '', line)
    line = re.sub(r'\s*\([^)]*\)', '', line)  # Remove parentheticals
    line = re.sub(r'\s*\*.*$', '', line)       # Remove asterisk and trailing text
    line = re.sub(r'\s+at\s+', ' @ ', line, flags=re.IGNORECASE)
    return line

def get_country(state):
    """Return the full country name based on the provided state abbreviation."""
    if state is None:
        return "United States"
    state = state.strip().upper()  # Force state abbreviation to uppercase
    if state in CANADIAN_PROVINCES:
        return "Canada"
    elif state in US_STATES:
        return "United States"
    elif state in COUNTRY_MAPPING:
        return COUNTRY_MAPPING.get(state, "Unknown Country")
    else:
        return "United States"

def parse_date_line(line):
    """
    Attempt to extract date components from a cleaned line.
    Returns a dictionary with keys: month, day, city, state, country, venue, and full_text.
    """
    for pattern in EXTRACT_PATTERNS:
        match = pattern.match(line)
        if match:
            groups = match.groups()
            try:
                month = int(groups[0])
                day = int(groups[1])
                # Adjust month if zero as per original logic
                if month == 0:
                    month = 10
            except ValueError:
                continue

            city = state = venue = None
            country = None

            if len(groups) >= 5 and groups[2] and groups[3] and groups[4]:
                # Pattern with city, state, and venue
                city = groups[2]
                state = groups[3]
                venue = groups[4]
                country = get_country(state)
            elif len(groups) >= 4 and groups[2] and groups[3]:
                # Pattern with city and venue (state not provided)
                city = groups[2]
                venue = groups[3]
                country = "United States"
            elif len(groups) >= 3:
                # Pattern with location info only; try to split into city and state
                location = groups[2]
                if ',' in location:
                    parts = [part.strip() for part in location.split(',', 1)]
                    city = parts[0]
                    state = parts[1] if len(parts) > 1 else None
                    country = get_country(state) if state else "United States"
                    if len(groups) > 3:
                        venue = groups[3]
                else:
                    city = location.strip()
                    country = "United States"
            return {
                "month": month,
                "day": day,
                "city": city.strip() if city else None,
                "state": state.strip().upper() if state else None,
                "country": country,
                "venue": venue.strip() if venue else None,
                "full_text": line.strip()
            }
    return None

def extract_tour_dates(content, tour_start=None, tour_end=None):
    """Extract tour dates from HTML content by parsing paragraphs and line breaks."""
    soup = BeautifulSoup(content, "html.parser")
    dates = []
    seen_dates = set()

    for p in soup.find_all('p'):
        # Split content on line breaks; handle both text nodes and tags.
        lines = []
        for elem in p.contents:
            if isinstance(elem, str):
                lines.extend(elem.splitlines())
            else:
                lines.extend(elem.get_text(separator='\n').splitlines())
        for line in lines:
            line = clean_line(line)
            if not line or not re.search(r'\d{1,2}[/.-]\d{1,2}', line):
                continue
            date_info = parse_date_line(line)
            if date_info:
                key = f"{date_info['month']}-{date_info['day']}-{date_info['city']}"
                if key not in seen_dates:
                    seen_dates.add(key)
                    dates.append(date_info)
    return dates

def parse_date(date_str):
    """
    Convert a date string in various formats (ISO, MM/DD/YY, MM/DD) to ISO format.
    Assumes current year for MM/DD format and adjusts two-digit years.
    """
    if not date_str:
        return None
    if isinstance(date_str, str) and 'T' in date_str:
        return date_str
    for fmt in ('%Y-%m-%d', '%m/%d/%y', '%m/%d'):
        try:
            dt = datetime.strptime(date_str, fmt)
            if fmt == '%m/%d':
                dt = dt.replace(year=datetime.now().year)
            elif fmt == '%m/%d/%y' and dt.year < 2000:
                dt = dt.replace(year=dt.year + 2000)
            return dt.isoformat()
        except (ValueError, TypeError):
            continue
    return None

def process_dates(data):
    """Iterate through tour entries to update start, end, and detailed tour dates."""
    for item in data:
        tour_dates = extract_tour_dates(item.get('content', ''))
        if tour_dates:
            iso_dates = []
            current_year = datetime.now().year
            for date_obj in tour_dates:
                try:
                    dt = datetime(current_year, date_obj['month'], date_obj['day'])
                    iso_dates.append(dt.isoformat())
                except (ValueError, TypeError) as e:
                    print(f"Error converting date: {date_obj} - {str(e)}")
            if iso_dates:
                iso_dates.sort()
                item['tour_start'] = iso_dates[0]
                item['tour_end'] = iso_dates[-1]
                item['tour_dates'] = tour_dates
            else:
                start = parse_date(item.get('tour_start'))
                end = parse_date(item.get('tour_end'))
                item['tour_start'] = start if start else None
                item['tour_end'] = end if end else None
        else:
            start = parse_date(item.get('tour_start'))
            end = parse_date(item.get('tour_end'))
            item['tour_start'] = start if start else None
            item['tour_end'] = end if end else None
    return data

def main():
    """Main function to load tour data, process dates, run regex tests, and write outputs."""
    # Load existing tour data
    with open("tour_data.json", "r") as f:
        data = json.load(f)
    
    dates_not_found = []
    processed_data = []
    
    # Process each tour entry
    for entry in data:
        print(f"\nProcessing: {entry.get('title', 'Untitled')}")
        tour_dates = extract_tour_dates(entry.get("content", ""), entry.get("tour_start"), entry.get("tour_end"))
        entry["tour_dates"] = tour_dates
        print(f"Found {len(tour_dates)} dates")
        
        parsed_start = parse_date(entry.get("tour_start"))
        parsed_end = parse_date(entry.get("tour_end"))
        if tour_dates or (parsed_start and parsed_end):
            if entry.get('country') == 'AUS':
                entry['country'] = 'Australia'
            processed_data.append(entry)
        else:
            dates_not_found.append(entry)
    
    # Test regex patterns against specific date strings
    date_test_cases = [
        "9/7 Columbus, OH @ Ace Of Cups",
        "9/8 Baltimore, MD @ Ottobar",
        "9/9 Alton, VA @ Blue Ridge Rock Fest*",
        "9/10 Philadelphia, PA @ Kung Fu Necktie",
        "9/11 Morgantown, WV @ Pleasant Street*",
        "9/13 Fresno, CA @ Strummer's",
        "9/14 Santa Cruz, CA @ The Atrium",
        "9/15 Sacramento, CA @ Goldfield Trading Post",
        "9/16 Portland, OR @ Mano Oculta PDX",
        "9/17 Seattle, WA @ El Corazon"
    ]
    
    for test_case in date_test_cases:
        print(f"\nTesting: {test_case}")
        for pattern in TEST_PATTERNS:
            if pattern.match(test_case):
                print(f"Matched pattern: {pattern.pattern}")
    
    # Simulated content for Zao and Warbringer
    zao_content = (
        "<p>Zao has announced a handful of shows with Thoughtcrimes leading up to their appearance at Blue Ridge Rock Festival in September. "
        "Tickets are available here.</p><p>Dates for Zao and Thoughtcrimes are:<br>"
        "9/7 Columbus, OH @ Ace Of Cups<br>"
        "9/8 Baltimore, MD @ Ottobar<br>"
        "9/9 Alton, VA @ Blue Ridge Rock Fest*<br>"
        "9/10 Philadelphia, PA @ Kung Fu Necktie<br>"
        "9/11 Morgantown, WV @ Pleasant Street*</p>"
    )
    
    warbringer_content = (
        "<p>Warbringer just announced the 'U.S. Unraveling 2022' West Coast tour to finally support their 2020 release Weapons of Tomorrow and will be joined by Heathen and Misfire.</p>"
        "<p>'U.S. Unraveling 2022' dates:<br>"
        "9/13 Fresno, CA @ Strummer's<br>"
        "9/14 Santa Cruz, CA @ The Atrium<br>"
        "9/15 Sacramento, CA @ Goldfield Trading Post<br>"
        "9/16 Portland, OR @ Mano Oculta PDX<br>"
        "9/17 Seattle, WA @ El Corazon<br>"
        "9/18 Boise, ID @ The Shredder<br>"
        "9/19 Denver, CO @ HQ<br>"
        "9/21 Lincoln, NE @ 1867 Bar<br>"
        "9/22 Oklahoma City, OK @ 89th St. Collective<br>"
        "9/23 Dallas, TX @ Amplified Live<br>"
        "9/24 Austin, TX @ Come and Take It Live<br>"
        "9/25 Albuquerque, NM @ Launchpad<br>"
        "9/26 El Paso, TX @ Rockhouse Bar &amp; Grill<br>"
        "9/28 Las Vegas, NV @ Backstage Bar<br>"
        "9/29 San Diego, CA @ Brick By Brick<br>"
        "9/30 Anaheim, CA @ Doll Hut<br>"
        "10/1 West Hollywood, CA @ Whisky-A-Go-Go</p>"
    )
    
    def normalize_content(html_content):
        """Normalize HTML content to plain text by replacing certain tags with newlines."""
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all(['br', 'p', 'center', 'div']):
            tag.replace_with('\n' + tag.get_text() + '\n')
        text = soup.get_text()
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    text_zao = normalize_content(zao_content)
    text_warbringer = normalize_content(warbringer_content)
    
    for pattern in TEST_PATTERNS:
        if pattern.match(text_zao):
            print("\nZao date matched:", text_zao)
        if pattern.match(text_warbringer):
            print("\nWarbringer date matched:", text_warbringer)
    
    # Process new sample data
    new_data = [
        {
            "id": 36984,
            "title": "Machine Head release intimate tour dates for U.S.",
            "image_path": "tour_images/36984.jpg",
            "content": "<p>Official press release:</p>...",
            "tour_start": "2022-11-03T00:00:00",
            "tour_end": "2022-12-23T00:00:00",
            "tags": ["Machine Head"],
            "tour_dates": []
        }
    ]
    
    processed_new_data = process_dates(new_data)
    print("\nProcessed new data:")
    print(processed_new_data)
    
    # Ensure the country field is set to "United States" for tour dates with valid US states.
    for entry in processed_data:
        for date in entry.get("tour_dates", []):
            state_val = date.get("state")
            if state_val and state_val.strip().upper() in US_STATES:
                date["country"] = "United States"
    
    # Write processed data to files
    with open("tour_data_processed.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    
    with open("tour_data_not_found.json", "w") as f:
        json.dump(dates_not_found, f, indent=4)
    
    print(f"\nCompleted processing dates:")
    print(f"- {len(processed_data)} entries with dates saved to tour_data_processed.json")
    print(f"- {len(dates_not_found)} entries where dates weren't found saved to tour_data_not_found.json")
    
    # Verify by reading back the processed data
    with open("tour_data_processed.json", "r") as f:
        processed_entries = json.load(f)
        print(f"Processed {len(processed_entries)} entries.")

if __name__ == "__main__":
    main()
