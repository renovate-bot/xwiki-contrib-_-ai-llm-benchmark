#!/usr/bin/env python3

import argparse
import json
import os
import re
import time

import httpx
from urllib.parse import urljoin
import markdownify
import bs4


def download_and_extract(client, url):
    # Download the HTML
    response = client.get(url)
    response.raise_for_status()  # Ensure the request was successful

    return response.text


def generate_json(reference, url, title, content):
    return {
        'id': reference,
        'url': url,
        'title': title,
        'collection': 'Eval',
        'mimetype': 'text/markdown',
        'language': 'en',
        'content': content
    }


def save_json_to_file(json_obj, filename):
    with open(filename, 'w') as file:
        json.dump(json_obj, file)


def main(urls):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }
    with httpx.Client(headers=headers) as client:
        for url in urls:
            try:
                html_content = download_and_extract(client, url)

                # Extract the data-xwiki-reference attribute on the html element
                parsed_html = bs4.BeautifulSoup(html_content, 'html.parser')
                reference = parsed_html.find('html')['data-xwiki-reference']

                print(f"Extracted reference: {reference}")

                # Extract the title from the HTML
                title = parsed_html.find('title').text.strip()

                # Remove (XWiki.org) from the end of the title
                title = re.sub(r'\s*\(XWiki\.org\)\s*$', '', title)
                print(f"Extracted title: {title}")

                # Convert the contents of the #xwikicontent div to XWiki syntax
                content_html = parsed_html.find(id='xwikicontent')
                if content_html is None:
                    raise ValueError("Could not find content in HTML")

                # Iterate over all links in the content and make them absolute
                for link in content_html.find_all('a'):
                    if 'href' in link.attrs:
                        link['href'] = urljoin(url, link['href'])

                # Iterate over all images and make their source URLs absolute
                for image in content_html.find_all('img'):
                    image['src'] = urljoin(url, image['src'])

                markdown_content = markdownify.markdownify(str(content_html), heading_style="ATX")

                # Generate the JSON object
                json_obj = generate_json(reference, url, title, markdown_content)

                # Save the JSON object to a file
                save_json_to_file(json_obj, get_filename(reference))

                print(f"Saved JSON for {reference} to file.")

                # Wait two seconds after every URL.
                time.sleep(2)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")

def get_filename(reference):
    # For the filename, remove any slashes and colons and replace them with underscores
    filename = reference.replace('/', '_').replace(':', '_')
    return f"context_data/documents/{filename}.json"


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description="Download one or several XWiki pages and convert them to JSON "
                                                    "with Markdown content.")
    arguments.add_argument('input', metavar='INPUT', type=str, nargs='+',
                           help="One or more URLs or a file containing URLs.")
    args = arguments.parse_args()

    arg_urls = []
    for input_value in args.input:
        if os.path.isfile(input_value):
            with open(input_value, 'r') as f:
                # Read all lines from the file, strip whitespace and remove empty lines
                arg_urls.extend([line.strip() for line in f.readlines() if line.strip()])
        else:
            arg_urls.append(input_value)

    main(arg_urls)
