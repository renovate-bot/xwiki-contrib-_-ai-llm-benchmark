import os
import json
import argparse
import sys

# Add the project's root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.models_connections.waise_model import WaiseModel

def translate_content(content, target_language, model):
    prompt = f"Translate the following text to {target_language}:\n\n{content} but keep any special syntax and links the same."
    try:
        response = model.invoke(prompt)
        print(f"Raw response: {response}")
        if isinstance(response, dict) and 'choices' in response:
            translated_content = response['choices'][0]['message']['content']
        elif isinstance(response, str):
            translated_content = response
        else:
            print(f"Unexpected response format: {response}")
            return content  # Return original content if translation fails
        return translated_content
    except Exception as e:
        print(f"Error during translation: {e}")
        return content  # Return original content if translation fails

def translate_documents(language, collection):
    source_dir = 'context_data/documents'
    
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    # Initialize the WaiseModel
    model = WaiseModel(model="AI.Models.GPT-4o", temperature=0.3, stream=False, verbose=True)

    # Iterate through all files in the source directory
    for filename in os.listdir(source_dir):
        if filename.endswith('.json'):
            source_path = os.path.join(source_dir, filename)
            dest_filename = f"{language}.{filename}"
            dest_path = os.path.join(source_dir, dest_filename)

            # Read the source JSON file
            with open(source_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Modify the language and collection
            data['language'] = language
            data['collection'] = collection

            # Translate the content
            print(f"Translating content for {filename}...")
            data['content'] = translate_content(data['content'], language, model)

            # Write the modified JSON to the new file
            with open(dest_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            print(f"Created: {dest_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate document metadata and content.")
    parser.add_argument('language', help="Target language code")
    parser.add_argument('collection', help="Target collection name")
    
    args = parser.parse_args()

    translate_documents(args.language, args.collection)
    print("Translation complete.")
