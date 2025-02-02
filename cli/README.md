# Screpa

Screpa is a web scraping tool that allows you to scrape company information from Xing. It is written in Python and uses playwright and BeautifulSoup.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Features](#features)

## Requirements

- [Python 3.7+](https://www.python.org/downloads/)
- A valid Xing account

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install playwright beautifulsoup4
playwright install chromium
```

## Usage

1. Set up your environment variables:

You can set up your environment variables in your shell like this:

- Linux/MacOS:

```bash
export XING_EMAIL="your-xing-email"
export XING_PASSWORD="your-xing-password"
```

- Windows:

```bash
set XING_EMAIL="your-xing-email"
set XING_PASSWORD="your-xing-password"
```

OR you can create a `.env` file in the root directory of the project and add the following lines:

```env
XING_EMAIL=your-xing-email
XING_PASSWORD=your-xing-password
```

then run the command below to load the environment variables from the `.env` file:

```bash
source .env
```

2. Run the script:

Basic usage:

```bash
python3 screpa.py
```

Advanced usage with arguments:

```bash
python3 screpa.py "search keyword" number_of_pages
```

Examples:

- Search for "real estate" companies across 2 pages (default)

```bash
python3 screpa.py
```

- Search for "software" companies across 5 pages

```bash
python3 screpa.py "software" 5
```

Search for "software" companies across 2 pages

```bash
python3 screpa.py "software"
```

## Features

- Automated login to Xing
- Company search with configurable keywords
- Multi-page result scraping
- Extracts:
  - Company names
  - Location information
  - Employee counts
  - XING member counts
  - Company websites
  - Contact emails
- Automatic HTML caching
- CSV export of results
- Privacy consent handling
- Retry mechanisms for failed requests

## Output

Results are saved in two formats:

1. Raw HTML files in the `results/` directory
2. Processed data in `screpa_leads.csv` file with the following columns:
   - company_name
   - xing_members
   - location
   - employee_count
   - profile_url
   - email
   - website
