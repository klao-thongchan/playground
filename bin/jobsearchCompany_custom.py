from serpapi import GoogleSearch
import json

class JobScrapeQueryRun:
    """
    Class for scraping job listings from Google using the SerpApi library.

    Attributes:
        - api_key (str): API key used for accessing the SerpApi service.
    """

    def __init__(self, api_key):
        """
        Initialize JobScrapeQueryRun.

        Args:
            api_key (str): API key used for accessing the SerpApi service.
        """
        self.api_key = api_key

    def scrape_google_jobs_listing(self, job_ids):
        """
        Scrapes individual job listings from Google based on job IDs.

        Args:
            job_ids (list): List of job IDs to scrape.

        Returns:
            list: List containing scraped job data for each job ID.
        """
        data = []

        for job_id in job_ids:
            params = {
                'api_key': self.api_key,
                'engine': 'google_jobs_listing',
                'q': job_id,
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            data.append({
                'job_id': job_id,
                'apply_options': results.get('apply_options'),
                'salaries': results.get('salaries'),
                'ratings': results.get('ratings')
            })

        return data
    
def extract_multiple_jobs(self):
    """
    Extracts multiple job listings from Google based on a search query.

    Returns:
        str: JSON-formatted string containing scraped job data for multiple listings.
    """
    params = {
        'api_key': self.api_key,
        'engine': 'google_jobs',
        'gl': 'us',
        'hl': 'en',
        'q': 'barista new york',
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    job_ids = [job.get('job_id') for job in results['jobs_results']]

    return json.dumps(self.scrape_google_jobs_listing(job_ids), indent=2, ensure_ascii=False)