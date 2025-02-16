# Metal Tour Dates Dataset v0.1

A dataset of metal, hardcore, and punk tour dates extracted from news announcements on Lambgoat. This is a work in progress.

## Contents

- `data.json` - Processed tour announcements with extracted dates and venue information
- `tour_images/` - Associated announcement images

## Data Format

Each entry contains:

- `id` - Unique identifier
- `title` - Tour announcement title
- `content` - Original announcement text
- `tour_start` - Start date of tour
- `tour_end` - End date of tour
- `image_path` - Path to announcement image
- `tags` - Associated bands
- `tour_dates` - Array of extracted dates containing:
  - `month` - Numeric month
  - `day` - Day of month
  - `city` - City name
  - `state` - State/province code
  - `country` - Full country name
  - `venue` - Venue name
  - `full_text` - Original date line text

## Work in Progress

This initial release focuses on basic date and venue extraction. Future updates will improve:
- Date parsing accuracy
- Venue name standardization
- Band categorization
- Historical data coverage

## Source

Data extracted from Lambgoat news articles using Python. Processing scripts available at [GitHub repo link]. 