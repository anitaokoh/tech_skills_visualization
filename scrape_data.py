import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import logging
import logging.config
import yaml

with open('logging.yaml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


data = []

def populate_urls(first_page):
    url_list = []
    page_number = 0
    url_list.append(first_page)
    for _ in range(9):
        page_number +=25
        url_list.append(first_page +'&start='+ str(page_number))
    return url_list

def linkedin_scraper(webpage):
        response = requests.get(str(webpage))
        soup = BeautifulSoup(response.content, 'html.parser')
        jobs = soup.find_all(
                                'div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
        for job in jobs:
            job_title = job.find('h3', class_='base-search-card__title').text.strip()
            job_post_date = job.find(
                                    'time', class_='job-search-card__listdate')['datetime'] if job.find(
                                    'time', class_='job-search-card__listdate') is not None else job.find(
                                    'time', class_='job-search-card__listdate--new')['datetime']
            job_page_link = job.find('a', class_='base-card__full-link')['href']
            resp = requests.get(job_page_link)
            sp = BeautifulSoup(resp.content, 'html.parser')
            job_description = sp.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5').text.strip(
                                ) if sp.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5') is not None else "Nan"
            data.append([job_title, job_post_date, job_page_link, job_description])
            time.sleep(3)
        return data 
            
def run_scrapper(first_page):
    start_time = time.time()
    url_list = populate_urls(first_page)
    logger.debug(f"There are {str(len(url_list))} links and {str(len(set(url_list)))} district links")
    count = 0
    for url in url_list:
        data = linkedin_scraper(url)
        count += 1
        logger.info(f"Completed url {str(count)}")
    logger.info("Scrapping data , Complete")
    df = pd.DataFrame(data, columns = ['job_title', 'job_post_date', 'job_page_link', 'job_description'])
    row_count_b4_deduplication = df.shape[0]
    logger.debug(f"There are {str(row_count_b4_deduplication)} rows before de-duplication")
    df = df.drop_duplicates()
    row_count_af_deduplication = df.shape[0]
    if row_count_b4_deduplication != row_count_af_deduplication:
        logger.warning(f"There are {str(row_count_b4_deduplication -row_count_af_deduplication)} rows less after deduplication")
    rows_with_na = df[df['job_description'].isna()].shape[0]
    if rows_with_na > 0:
        logger.warning(f"There are {str(rows_with_na)} job description rows with null job description")
        df = df.dropna(subset=['job_description']) 
        logger.warning(f"There are now {str(df.shape[0])} rows returned")
    end_time = time.time()
    logger.info(f"Completed at {str(end_time - start_time)} seconds")
    return df

if __name__ == '__main__':
    ## default link
    first_page = 'https://www.linkedin.com/jobs/search/?currentJobId=3433766873&f_JT=F&f_T=25206&geoId=101282230&keywords=machine%20learning%20engineer&location=Germany&refresh=true&sortBy=R'
    df = run_scrapper(first_page)
    