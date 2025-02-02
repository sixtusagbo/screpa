#!/bin/env python3
"""Screpa is a web scraping tool for Xing company search results"""

import os
import re
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


class Screpa:
    def __init__(self):
        self.base_url = "https://www.xing.com"
        self.has_accepted_privacy = False
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)

    def handle_privacy_consent(self, page, max_attempts=3):
        """Try to handle privacy consent dialog multiple times"""
        for i in range(max_attempts):
            try:
                consent_button = page.get_by_role("button", name="Accept all")
                if consent_button.is_visible(timeout=2000):
                    consent_button.click()
                    print("Privacy consent accepted on attempt", i + 1)
                    time.sleep(1)
                    self.has_accepted_privacy = True
                    return True
            except:
                time.sleep(2)  # Wait before next attempt
        return False

    def login(self, page):
        """Handle Xing login with environment credentials"""
        try:
            page.goto(
                "https://login.xing.com/?locale=en",
                timeout=120000,
            )

            # Initial cookie consent
            self.handle_privacy_consent(page)

            # Fill login form
            page.fill('input[name="username"]', os.getenv("XING_EMAIL"))
            page.fill('input[name="password"]', os.getenv("XING_PASSWORD"))
            page.click('button:has-text("Log in")')

            # Wait longer after login to ensure full page load
            time.sleep(5)

            # Check for privacy consent again after login
            if not self.has_accepted_privacy:
                self.handle_privacy_consent(page)

            # Wait for navigation to complete
            page.wait_for_load_state("networkidle", timeout=30000)

            # One final check for privacy consent
            if not self.has_accepted_privacy:
                self.handle_privacy_consent(page)

        except Exception as e:
            print(f"Login process error: {str(e)}")
            raise

    def navigate_with_retry(self, page, url, max_retries=3):
        """Navigate to URL with retry mechanism"""
        for attempt in range(max_retries):
            try:
                response = page.goto(
                    url,
                    timeout=120000,
                    wait_until="networkidle",
                )
                if response and response.ok:
                    return True

                time.sleep(5 * (attempt + 1))  # Incremental backoff

            except Exception as e:
                print(f"Navigation attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5 * (attempt + 1))
        return False

    def extract_search_results(self, html: str) -> List[Dict]:
        """Extract basic company info from search results page"""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Updated selector - looking for the search results list
        results_section = soup.find(
            "ol", {"class": "shared-styles__SearchList-sc-dfa70b15-3"}
        )
        if not results_section:
            print("No results section found")
            return results

        # Updated selector for company cards
        company_cards = results_section.find_all(
            "li", {"class": "shared-styles__SearchListElement-sc-dfa70b15-4"}
        )

        print(f"Found {len(company_cards)} company cards")

        for card in company_cards:
            result_info = {
                "company_name": "",
                "xing_members": "",
                "location": "",
                "employee_count": "",
                "profile_url": "",
            }

            try:
                # Updated link selector
                link = card.find(
                    "a",
                    {
                        "class": "companies-search-results-styles__CompanyLinkWrapper-sc-5d3cf71d-1"
                    },
                )
                if link:
                    result_info["profile_url"] = self.base_url + link.get("href")

                # Updated company name selector
                name_tag = card.find(
                    "h2", {"class": "headline-styles__Headline-sc-339d833d-0"}
                )
                if name_tag:
                    result_info["company_name"] = name_tag.text.strip()

                # Updated company info selector - more specific class
                info_paragraphs = card.find_all(
                    "p", {"class": "body-copy-styles__BodyCopy-sc-b3916c1b-0"}
                )

                for p in info_paragraphs:
                    text = p.text.strip()
                    if "XING members:" in text:
                        result_info["xing_members"] = text.split("XING members:")[
                            1
                        ].strip()
                    elif "Employees:" in text:
                        result_info["employee_count"] = text.split("Employees:")[
                            1
                        ].strip()
                    elif text and ":" not in text:  # Location has no label
                        result_info["location"] = text

                # Only add if we have at least a name
                if result_info["company_name"]:
                    results.append(result_info)

            except Exception as e:
                print(f"Error processing card: {str(e)}")
                continue

        return results

    def clean_profile_url(self, url: str) -> str:
        """Clean up malformed profile URLs"""
        if url.startswith(self.base_url + self.base_url):
            return url[len(self.base_url) :]
        return url

    def extract_company_contact(self, html: str) -> Dict[str, str]:
        """Extract contact info from company profile page HTML"""
        contact_info = {
            "website": "",
            "email": "",
        }

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find email and website combo
            # First look near mailto links as they're often paired
            email_link = soup.find("a", href=lambda x: x and x.startswith("mailto:"))
            if email_link:
                email = email_link["href"].replace("mailto:", "").strip()
                # Clean up any URL encoding or extra parameters
                email = email.split("?")[0].split("&")[0]
                contact_info["email"] = email
                print(f"Found email ${email}")

                # Look for website link near the email link
                parent = email_link.parent
                website_links = parent.find_all(
                    "a",
                    href=lambda x: x
                    and re.match(r"https?://(?:www\.)?[^/]+\.[^/]+", str(x)),
                )
                if website_links:
                    website = website_links[0]["href"].strip()
                    contact_info["website"] = website
                    print(f"Found paired email/website: {email} / {website}")
                    return contact_info

            # Fallback: Look for any website link with www
            website_link = soup.find(
                "a",
                href=lambda x: x and re.match(r"https?://www\.[^/]+\.[^/]+", str(x)),
            )
            if website_link:
                website = website_link["href"].strip()
                contact_info["website"] = website
                print(f"Found website: {website}")

        except Exception as e:
            print(f"Error extracting contact info: {str(e)}")

        return contact_info

    def scrape_company_profile(self, url: str) -> Dict[str, str]:
        """Scrape an individual company profile page"""
        if not url:
            return {}

        clean_url = self.clean_profile_url(url)
        url_hash = hash(clean_url)
        cached_file = self.results_dir / f"company_{url_hash}.html"

        if cached_file.exists():
            print(f"Using cached profile from {cached_file}")
            with open(cached_file, "r", encoding="utf-8") as f:
                return self.extract_company_contact(f.read())

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            try:
                if not self.navigate_with_retry(page, clean_url):
                    return {}

                time.sleep(5)  # Wait for dynamic content
                html_content = page.content()

                # Cache the profile page
                with open(cached_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                return self.extract_company_contact(html_content)

            except Exception as e:
                print(f"Error scraping company profile {clean_url}: {str(e)}")
                return {}
            finally:
                context.close()

    def click_show_more(self, page, clicks=2):
        """Click 'Show more' button multiple times to load more results"""
        for i in range(clicks):
            try:
                # Look for the "Show more" button with exact text
                show_more = page.get_by_role("button", name="Show more")
                if show_more.is_visible(timeout=5000):
                    show_more.click()
                    print(f"Clicked 'Show more' button ({i + 1}/{clicks})")
                    # Wait for new results to load
                    time.sleep(5)
                else:
                    print("No more results to load")
                    break
            except Exception as e:
                print(f"Error clicking 'Show more': {str(e)}")
                break

    def scrape_xing(self, keyword: str, pages: int = 3) -> List[Dict]:
        """Handle browser automation and HTML saving with pagination"""
        all_results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-features=site-per-process"],
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            try:
                self.login(page)

                search_url = f"https://www.xing.com/search/companies?keywords={keyword}"
                if not self.navigate_with_retry(page, search_url):
                    raise Exception("Failed to navigate to search results")

                # Wait for initial results to load
                time.sleep(5)

                # Process first page results
                html_content = page.content()
                initial_results = self.extract_search_results(html_content)
                all_results.extend(initial_results)
                print(f"Found {len(initial_results)} results on initial page")

                # Click "Show more" button for remaining pages
                for page_num in range(2, pages + 1):
                    print(f"Loading page {page_num}...")
                    try:
                        show_more = page.get_by_role("button", name="Show more")
                        if show_more.is_visible(timeout=5000):
                            show_more.click()
                            print(f"Clicked 'Show more' button for page {page_num}")
                            # Wait for new results to load
                            time.sleep(5)

                            # Extract results from new page
                            html_content = page.content()
                            page_results = self.extract_search_results(html_content)
                            new_results = [
                                r for r in page_results if r not in all_results
                            ]
                            all_results.extend(new_results)
                            print(
                                f"Found {len(new_results)} new results on page {page_num}"
                            )
                        else:
                            print("No more results to load")
                            break
                    except Exception as e:
                        print(f"Error loading page {page_num}: {str(e)}")
                        break

                # Save the final HTML content
                self.save_html_content(html_content)

            except Exception as e:
                print(f"Scraping error: {str(e)}")
                if "html_content" in locals():
                    self.save_html_content(
                        html_content, f"xing_error_{int(time.time())}.html"
                    )
            finally:
                context.close()

        # Process contact info for all results with progress tracking
        total_companies = len(all_results)
        print(f"\nProcessing contact info for {total_companies} companies...")
        for idx, result in enumerate(all_results, 1):
            if result.get("profile_url"):
                print(
                    f"\rFetching contact info for {result['company_name']} ({idx}/{total_companies})",
                )
                contact_info = self.scrape_company_profile(result["profile_url"])
                result.update(contact_info)
        print("\nFinished fetching contact info")

        return all_results

    def save_to_csv(self, data: List[Dict]):
        """Save results to CSV file"""
        with open("screpa_leads.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "company_name",
                "xing_members",
                "location",
                "employee_count",
                "profile_url",
                "email",
                "website",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def save_html_content(self, html: str, filename: str = None):
        """Save HTML content to results directory with timestamp"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xing_search_{timestamp}.html"

        filepath = self.results_dir / filename
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved HTML content to {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving HTML content: {str(e)}")
            return None

    def get_most_recent_html(self) -> tuple[str, str]:
        """Get the most recently saved HTML file content"""
        html_files = list(self.results_dir.glob("xing_search_*.html"))
        if not html_files:
            return None, None

        latest_file = max(html_files, key=lambda x: x.stat().st_mtime)
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                return f.read(), str(latest_file)
        except Exception as e:
            print(f"Error reading HTML file: {str(e)}")
            return None, None


if __name__ == "__main__":
    required_envs = ["XING_EMAIL", "XING_PASSWORD"]
    if not all(os.getenv(e) for e in required_envs):
        print("Missing environment variables. Required:", required_envs)
        exit(1)

    scraper = Screpa()
    print("Screpa Lead Generator v1.0.0")

    keyword = "real estate"
    print(f"Searching for {keyword} companies...")

    try:
        results = scraper.scrape_xing(keyword, pages=3)
        scraper.save_to_csv(results)
        print(f"Saved {len(results)} leads")
        if results:
            print("Sample lead:", results[0])
    except Exception as e:
        print(f"Error: {str(e)}")
