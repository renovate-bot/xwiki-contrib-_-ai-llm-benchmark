#!/usr/bin/env python3

import argparse
import os.path

import httpx
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import time
import download_wiki_page

def download_space(client, url):
    # Download the URL and extract the data-xwiki-rest-url attribute on the HTML element (we don't care too much
    # about parsing HTML and just use the first one we find).
    response = client.get(url)
    response.raise_for_status()
    rest_url = response.text.split('data-xwiki-rest-url="')[1].split('"')[0]
    # Ensure that the URL ends with "/WebHome" and strip that part.
    if not rest_url.endswith("/WebHome"):
        raise ValueError(f"Expected REST URL to end with '/WebHome', but got '{rest_url}' - is the page not a space "
                         f"home?")
    rest_url = rest_url[:-8]

    # Add the domain of the url to the rest_url which is just the path.
    rest_url = urljoin(url, rest_url)

    page_size = 20
    start = 0

    while True:
        # Set the URL parameters number and start to the page_size and start variables
        params = {
            'number': page_size,
            'start': start
        }
        # Download the XML from the REST URL. It should have a pages root element with pageSummary elements inside,
        # extract the content of the xwikiAbsoluteUrl elements inside them. If there are no pageSummary elements,
        # abort the loop.
        response = client.get(rest_url, params=params)
        response.raise_for_status()
        xml_content = response.text
        root = ET.fromstring(xml_content)
        pages = root.findall('./{http://www.xwiki.org}pageSummary')

        if not pages:
            break

        urls = [page.find('{http://www.xwiki.org}xwikiAbsoluteUrl').text for page in pages
                # Skip already downloaded pages.
                if not output_exists(page.find('{http://www.xwiki.org}id').text)]
        download_wiki_page.main(urls)

        start += page_size

        # Wait two seconds before requesting the next page to avoid creating too much load on the server.
        time.sleep(2)

def output_exists(reference):
    return os.path.exists(download_wiki_page.get_filename(reference))

def main(urls):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0'
    }
    with httpx.Client(headers=headers) as client:
        for url in urls:
            print(f"Downloading {url}")
            download_space(client, url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download all pages in a wiki space')
    parser.add_argument('urls', metavar='URL', type=str, nargs='+', help='URLs to spaces that shall be downloaded')
    args = parser.parse_args()

    main(args.urls)