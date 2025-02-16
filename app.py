import os
import re
import requests
import pymssql
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import json

# Database credentials
DB_CONFIG = {
    "server": "s11.everleap.com",
    "user": "website",
    "password": "toyotaFord777$",
    "database": "DB_6729_lambgoat",
    "port": 1433
}

# Create folders for storing images and data
IMAGE_DIR = "tour_images"
DATA_FILE = "tour_data.json"

os.makedirs(IMAGE_DIR, exist_ok=True)

# Regular expression to find tour dates
DATE_PATTERN = r"""
    # Full dates like "January 15, 2024" or "Jan 15, 2024"
    (?:\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|
    Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)
    \s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b)
    |
    # Dates like MM/DD/YYYY or MM/DD/YY
    (?:\b\d{1,2}/\d{1,2}/(?:\d{4}|\d{2})\b)
    |
    # Dates like "15th of January, 2024"
    (?:\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?
    (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|
    Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)
    (?:\s+\d{4})?\b)
"""

# Connect to database
def fetch_tour_articles():
    connection = pymssql.connect(**DB_CONFIG)
    cursor = connection.cursor(as_dict=True)

    query = """
    SELECT 
        n.Id, 
        n.Title, 
        n.NewsContent, 
        n.TourStartDate, 
        n.TourEndDate,
        STRING_AGG(t.Title, ',') as Tags
    FROM NewsItems n
    LEFT JOIN NewsItemTag nit ON n.Id = nit.NewsItemId
    LEFT JOIN Tags t ON nit.TagId = t.Id
    WHERE n.TourStartDate IS NOT NULL AND n.TourEndDate IS NOT NULL
    GROUP BY n.Id, n.Title, n.NewsContent, n.TourStartDate, n.TourEndDate;
    """
    cursor.execute(query)
    articles = cursor.fetchall()
    total = len(articles)
    print(f"Found {total} articles to process")
    connection.close()
    
    return articles

# Extract first image URL from HTML content
def extract_first_image(content):
    soup = BeautifulSoup(content, "html.parser")
    img_tag = soup.find("img")
    if not img_tag or not img_tag.get('src'):
        return None
        
    src = img_tag['src']
    # Handle relative URLs
    if src.startswith('/cdn/'):
        return f"https://lambgoat.com{src}"
    return src

# Extract tour dates from content
def extract_tour_dates(content):
    # Clean the content first
    content = BeautifulSoup(content, "html.parser").get_text()
    
    # Find all dates using the expanded pattern
    matches = re.finditer(DATE_PATTERN, content, re.VERBOSE)
    dates = [match.group().strip() for match in matches]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_dates = [x for x in dates if not (x in seen or seen.add(x))]
    
    return unique_dates if unique_dates else None

# Download and save image
def download_image(image_url, image_id):
    try:
        # Add headers to avoid rate limiting
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Skip malformed URLs
        if '?' in image_url and not image_url.endswith('?'):
            image_url = image_url.split('?')[0]
            
        response = requests.get(image_url, timeout=10, headers=headers)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img_path = os.path.join(IMAGE_DIR, f"{image_id}.jpg")
        img.save(img_path)
        print(f"Successfully downloaded: {image_url}")
        return img_path
    except Exception as e:
        print(f"Failed to download {image_url}: {e}")
        return None

# Main function
def main():
    # Load existing dataset for image paths
    existing_data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                existing_data = {item['id']: item for item in json.load(f)}
            except json.JSONDecodeError:
                existing_data = {}

    articles = fetch_tour_articles()
    dataset = []
    total = len(articles)

    for i, article in enumerate(articles, 1):
        print(f"\nProcessing article {i}/{total}: {article['Title']}")
        image_url = extract_first_image(article["NewsContent"])

        if image_url:
            # Reuse existing image if available
            if article["Id"] in existing_data and os.path.exists(existing_data[article["Id"]]["image_path"]):
                image_path = existing_data[article["Id"]]["image_path"]
                print(f"Reusing existing image for: {article['Title']}")
            else:
                image_path = download_image(image_url, article["Id"])

            if image_path:
                # Convert datetime objects to strings
                tour_start = article["TourStartDate"].isoformat() if article["TourStartDate"] else None
                tour_end = article["TourEndDate"].isoformat() if article["TourEndDate"] else None
                
                dataset.append({
                    "id": article["Id"],
                    "title": article["Title"],
                    "image_path": image_path,
                    "content": article["NewsContent"],
                    "tour_start": tour_start,
                    "tour_end": tour_end,
                    "tags": article["Tags"].split(',') if article["Tags"] else []
                })
                
                # Save after each successful article
                with open(DATA_FILE, "w") as f:
                    json.dump(dataset, f, indent=4)
                print(f"Saved progress: {len(dataset)} records")

    print(f"Completed saving {len(dataset)} tour records to {DATA_FILE}")

if __name__ == "__main__":
    main()
