import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import unicodedata

def extract_tour_dates(content, tour_start=None, tour_end=None):
    # Clean the content first - remove HTML and get text
    soup = BeautifulSoup(content, "html.parser")
    
    # Replace <br> and other tags with newlines
    for tag in soup.find_all(['br', 'p', 'center', 'div']):
        tag.replace_with('\n' + tag.get_text() + '\n')
    text = soup.get_text()
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Clean up unicode line separators and other special chars
    text = text.replace('\u2028', '\n')
    text = text.replace('\u2029', '\n')
    text = text.replace('\u200b', '')  # zero-width space
    text = text.replace('\xa0', ' ')   # non-breaking space
    
    # Clean up common HTML entities
    text = re.sub(r'&[a-z]+;', ' ', text)
    
    # Add patterns for dates with full year and different separators
    us_pattern = r'^(?:1[0-2]|0?[1-9])[-/.](\d{1,2})(?:[-/.]\d{2,4})?\s+(.*?),\s*(\w{2,3})(?:(?:\s*@\s*|\s+)(.+?))?(?:\s*[*#$%].*?)?(?:\s*\(.*?\))?(?:\s*$)'
    
    # International Pattern: More flexible format
    intl_pattern = r'^(?:1[0-2]|0?[1-9})[-/.](\d{1,2})(?:[-/.]\d{2,4})?\s+(.*?),\s*([A-Z]{2,3}|[A-Z][a-z]+)(?:(?:\s*@\s*|\s+)(.+?))?(?:\s*[*#$%].*?)?(?:\s*\(.*?\))?(?:\s*$)'
    
    # Venue pattern for cases with just @ separator
    venue_pattern = r'^(?:1[0-2]|0?[1-9})[-/.](\d{1,2})(?:[-/.]\d{2,4})?\s+(.*?)(?:\s*@\s*|\s+)(.+?)(?:\s*[*#$%].*?)?(?:\s*\(.*?\))?(?:\s*$)'
    
    # Country code mappings
    country_codes = {
        'UK': 'United Kingdom',
        'GB': 'United Kingdom',
        'DE': 'Germany',
        'FR': 'France',
        'ES': 'Spain',
        'IT': 'Italy',
        'NL': 'Netherlands',
        'BE': 'Belgium',
        'SE': 'Sweden',
        'DK': 'Denmark',
        'NO': 'Norway',
        'FI': 'Finland',
        'PT': 'Portugal',
        'IE': 'Ireland',
        'AU': 'Australia',
        'NZ': 'New Zealand',
        'JP': 'Japan',
        'CA': 'Canada',
        'ON': 'Canada',  # Ontario
        'QC': 'Canada'   # Quebec
    }
    
    # Additional cleanup for lines
    def clean_line(line):
        line = line.strip()
        line = re.sub(r'\s+', ' ', line)  # normalize spaces
        line = re.sub(r'&nbsp;', ' ', line)  # remove &nbsp;
        line = re.sub(r'\s*,\s*$', '', line)  # remove trailing comma
        line = re.sub(r'\s*\*.*$', '', line)  # remove asterisk notes
        line = re.sub(r'\s{2,}', ' ', line)  # remove double spaces
        line = re.sub(r'(?i)dates?:?\s*', '', line)  # remove "Date:" prefixes
        line = re.sub(r'(?i)tour\s+dates?:?\s*', '', line)  # remove "Tour dates:" prefixes
        line = re.sub(r'0$', '', line)  # remove trailing 0
        line = re.sub(r'(?i)with.*$', '', line)  # remove "with Band X" suffixes
        line = re.sub(r'\s*[*#$%].*$', '', line)  # remove support band markers
        return line
    
    # Split into lines and clean
    date_lines = []
    for line in text.split('\n'):
        line = clean_line(line)
        # Split on common date separators including dots
        parts = re.split(r'(?<=\d)\s*(?=(?:1[0-2]|0?[1-9])[-/.]\d{1,2})|(?<=\))\s*(?=(?:1[0-2]|0?[1-9})[-/.]\d{1,2})', line)
        for part in parts:
            part = part.strip()
            # Match date patterns more flexibly including dots
            if re.match(r'^(?:1[0-2]|0?[1-9})[-/.]\d{1,2}|\d{4}[-/.]\d{2}[-/.]\d{2}|\d{1,2}-\d{1,2}', part):
                date_lines.append(part)
    
    dates = []
    for line in date_lines:
        try:
            line = clean_line(line)
            if not line:
                continue
            
            # Try US pattern first
            us_match = re.match(us_pattern, line)
            if us_match:
                month, day, city, state, venue = us_match.groups()
                month = int(month)  # This will now correctly handle "10"
                if month == 0:  # Fix any zero months to be 10
                    month = 10
                # Check if it's actually a Canadian province
                if state.upper() in ['ON', 'QC']:
                    dates.append({
                        "month": month,
                        "day": int(day),
                        "city": city.strip(),
                        "state": state.strip(),
                        "country": "Canada",
                        "venue": venue.strip() if venue else None,
                        "full_text": line.strip()
                    })
                else:
                    dates.append({
                        "month": month,
                        "day": int(day),
                        "city": city.strip(),
                        "state": state.strip(),
                        "country": "United States",
                        "venue": venue.strip() if venue else None,
                        "full_text": line.strip()
                    })
                continue
            
            # Try international pattern
            intl_match = re.match(intl_pattern, line)
            if intl_match:
                date, city, country_code, venue = intl_match.groups()
                month, day = map(int, date.split('/'))
                country = country_codes.get(country_code.upper(), country_code)
                dates.append({
                    "month": month,
                    "day": day,
                    "city": city.strip(),
                    "state": None,
                    "country": country,
                    "venue": venue.strip() if venue else None,
                    "full_text": line.strip()
                })
                continue
            
            # Try venue pattern for cases without state/country
            venue_match = re.match(venue_pattern, line)
            if venue_match:
                month, day, location, venue = venue_match.groups()
                dates.append({
                    "month": int(month),
                    "day": int(day),
                    "location": location.strip(),
                    "venue": venue.strip() if venue else None,
                    "full_text": line.strip()
                })
                continue
            
            # Fallback for unmatched patterns
            print(f"Unmatched line: {line}")
            
        except Exception as e:
            print(f"Error parsing line: {line} - {e}")
    
    # Update month values for Slipknot tour dates
    for date in dates:
        if date["month"] == 0 and date["day"] >= 1 and date["day"] <= 31:
            date["month"] = 10
    
    return dates

def parse_date(date_str):
    # Handle empty/None dates
    if not date_str:
        return None
        
    # If already in ISO format, return as is
    if isinstance(date_str, str) and 'T' in date_str:
        return date_str

    try:
        # First try parsing with full year format
        return datetime.strptime(date_str, '%Y-%m-%d').isoformat()
    except (ValueError, TypeError):
        try:
            # Try parsing MM/DD/YY format
            dt = datetime.strptime(date_str, '%m/%d/%y')
            # Adjust years - if year is less than 50, assume it's 20xx, otherwise 19xx
            if dt.year < 2000:
                dt = dt.replace(year=dt.year + 2000)
            return dt.isoformat()
        except (ValueError, TypeError):
            try:
                # Try parsing MM/DD format and assume current year
                dt = datetime.strptime(date_str, '%m/%d')
                # Use current year for MM/DD format
                current_year = datetime.now().year
                dt = dt.replace(year=current_year)
                return dt.isoformat()
            except (ValueError, TypeError):
                return None

def process_dates(data):
    for item in data:
        # Extract dates from content
        dates = extract_tour_dates(item['content'])
        
        if dates:
            # Sort dates chronologically
            valid_dates = [d for d in dates if d is not None]
            if valid_dates:
                valid_dates.sort()
                # Set tour start/end dates
                item['tour_start'] = valid_dates[0]
                item['tour_end'] = valid_dates[-1]
            else:
                # If no valid dates found, try using existing tour_start/end
                start = parse_date(item.get('tour_start'))
                end = parse_date(item.get('tour_end'))
                if start and end:
                    item['tour_start'] = start
                    item['tour_end'] = end
                else:
                    # Set to None if no valid dates found
                    item['tour_start'] = None
                    item['tour_end'] = None
        else:
            # If no dates in content, try using existing tour_start/end
            start = parse_date(item.get('tour_start'))
            end = parse_date(item.get('tour_end'))
            if start and end:
                item['tour_start'] = start
                item['tour_end'] = end
            else:
                item['tour_start'] = None
                item['tour_end'] = None

    return data

def main():
    # Load existing data
    with open("tour_data.json", "r") as f:
        data = json.load(f)
    
    # Track different types of entries
    dates_not_found = []  # Failed to extract dates
    processed_data = []  # Successfully processed dates
    
    # Process each entry
    for entry in data:
        print(f"\nProcessing: {entry['title']}")
        tour_dates = extract_tour_dates(
            entry["content"],
            entry.get("tour_start"),
            entry.get("tour_end")
        )
        entry["tour_dates"] = tour_dates
        print(f"Found {len(tour_dates)} dates")
        
        # Sort entries based on whether they have dates
        if len(tour_dates) == 0:
            dates_not_found.append(entry)
        else:
            processed_data.append(entry)
    
    # Save processed data
    with open("tour_data_processed.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    
    # Save entries where dates weren't found
    with open("tour_data_not_found.json", "w") as f:
        json.dump(dates_not_found, f, indent=4)
    
    print(f"\nCompleted processing dates:")
    print(f"- {len(processed_data)} entries with dates saved to tour_data_processed.json")
    print(f"- {len(dates_not_found)} entries where dates weren't found saved to tour_data_not_found.json")

if __name__ == "__main__":
    main() 