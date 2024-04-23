import json
import os
import matplotlib.pyplot as plt

# Load and parse results data
def load_results(results_dir):
    results = []
    for filename in os.listdir(results_dir):
        if filename.endswith('_result.json'):
            result_file = os.path.join(results_dir, filename)
            with open(result_file, 'r') as file:
                result = json.load(file)
                results.append(result)
    return results

# Create plots directory if it doesn't exist
plots_dir = 'plots'
os.makedirs(plots_dir, exist_ok=True)

# Load results data
results_dir = 'results'
results = load_results(results_dir)

# Extract data for plotting
queries = [result['query'] for result in results]
relevance_scores = [result['relevance_score'] for result in results]
accuracy_scores = [result['accuracy']['rouge-1']['f'] for result in results]

# Create a bar plot for relevance scores
plt.figure(figsize=(10, 6))
plt.bar(queries, relevance_scores)
plt.xlabel('Query')
plt.ylabel('Relevance Score')
plt.title('Relevance Scores')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'relevance_scores.png'))
plt.close()

# Create a bar plot for accuracy scores (ROUGE-1 F-score)
plt.figure(figsize=(10, 6))
plt.bar(queries, accuracy_scores)
plt.xlabel('Query')
plt.ylabel('Accuracy Score (ROUGE-1 F-score)')
plt.title('Accuracy Scores')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'accuracy_scores.png'))
plt.close()

print("Plots saved in the 'plots' directory.")
