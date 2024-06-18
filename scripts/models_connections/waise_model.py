import os
import requests
import json
from dotenv import load_dotenv

class WaiseModel:
    def __init__(self, model="AI.Models.llama3", temperature=1, stream=False, verbose=False):
        # Load environment variables
        load_dotenv()

        # Initialize connection information and credentials
        self.wiki_name = os.getenv('WIKI_NAME')
        self.base_url = os.getenv('BASE_URL').format(wikiName=self.wiki_name)
        self.username = os.getenv('WAISE_USERNAME')
        self.password = os.getenv('WAISE_PASSWORD')
        self.auth = (self.username, self.password)

        # Initialize model configuration
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self.verbose = verbose

    def invoke(self, prompt):
        """Send a prompt to the WAISE model and return the response."""
        url = f'{self.base_url}/v1/chat/completions'
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "temperature": self.temperature,
            "stream": self.stream,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(url, headers=headers, json=data, auth=self.auth)
        if response.status_code == 200:
            try:
                response_data = response.json()
                if self.verbose:
                    return response_data
                else:
                    # Adjust this line based on the actual structure of the response
                    return response_data['choices'][0]['message']['content']
            except json.JSONDecodeError:
                raise Exception("Failed to decode JSON from response: " + response.text)
        else:
            error_message = f"Request failed with status code {response.status_code}: {response.text}"
            raise Exception(error_message)

# This allows the module to be used as a script for testing purposes
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Send a simple prompt to the WAISE API.')
    parser.add_argument('--prompt', required=True, help='Prompt to send to the model')
    parser.add_argument('--verbose', action='store_true', help='Return the full response')
    args = parser.parse_args()

    model = WaiseModel(verbose=args.verbose)
    result = model.invoke(args.prompt)
    print("Response from model:")
    print(json.dumps(result, indent=2) if args.verbose else result)
