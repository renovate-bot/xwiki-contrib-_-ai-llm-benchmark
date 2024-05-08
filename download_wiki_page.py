#!/usr/bin/env python3

import argparse
import json
import re
import requests
from urllib.parse import urlencode
import markdownify
import bs4


def download_and_extract(session, url):
    # Append query parameters
    url_with_params = f"{url}?{urlencode({'xpage': 'plain', 'htmlHeaderAndFooter': 'true'})}"

    # Download the HTML
    response = session.get(url_with_params)
    response.raise_for_status()  # Ensure the request was successful

    return response.text


def convert_html_to_xwiki_syntax(session, html_content):
    # Prepare the payload
    payload = {
        'text': html_content
    }

    # Send the request
    url = 'http://localhost:1620/xwiki/bin/view/Main/?sheet=CKEditor.HTMLConverter&fromHTML=true'
    # Get the form token
    response = session.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Extract the form token
    match = re.search(r'data-xwiki-form-token="([^"]+)"', response.text)
    if match:
        form_token = match.group(1)
    else:
        raise ValueError("Could not find form token")
    payload['formToken'] = form_token

    response = session.post(url, data=payload)
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
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    })

    for url in urls:
        try:
            html_content = download_and_extract(session, url)

            # Extract the data-xwiki-reference attribute on the html element
            parsed_html = bs4.BeautifulSoup(html_content, 'html.parser')
            reference = parsed_html.find('html')['data-xwiki-reference']

            print(f"Extracted reference: {reference}")

            # Extract the title from the HTML
            title = parsed_html.find('title').text.strip()

            # Remove (XWiki.org) from the end of the title
            title = re.sub(r'\s*\(XWiki\.org\)\s*$', '', title)
            print(f"Extracted title: {title}")

            # Convert the contents of the #xwikimaincontainerinner div to XWiki syntax
            content_html = parsed_html.find(id='xwikimaincontainerinner', recursive=True)
            if content_html is None:
                raise ValueError("Could not find content in HTML")
            markdown_content = markdownify.markdownify(str(content_html), heading_style="ATX")

            # Generate the JSON object
            json_obj = generate_json(reference, url, title, markdown_content)

            # For the filename, remove any slashes and colons and replace them with underscores
            filename = reference.replace('/', '_').replace(':', '_')

            # Save the JSON object to a file
            save_json_to_file(json_obj, f"context_data/documents/{filename}.json")

            print(f"Saved JSON for {reference} to file.")
        except Exception as e:
            print(f"Error processing URL {url}: {e}")


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description="Download one or several XWiki pages and convert them to JSON "
                                                    "with Markdown content.")
    arguments.add_argument('urls', metavar='URL', type=str, nargs='+', help="One or more URLs to process.")
    args = arguments.parse_args()

    main(args.urls)
