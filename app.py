import os
import requests
import re
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import time
import streamlit as st

# Load environment variables
load_dotenv()

# Set up Google Generative AI API credentials
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize ChatGoogleGenerativeAI
chat = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, convert_system_message_to_human=True)

# Function to fetch a GitHub user's repositories with rate limiting
def api_request_with_rate_limit(url, params=None):
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 429:  # Rate limit exceeded
            wait_time = int(response.headers.get('X-RateLimit-Reset', 60))  # Use rate limit reset header if available
            print(f"Rate limit exceeded, waiting for {wait_time} seconds.")
            time.sleep(wait_time + 10)  # Sleep and retry
        else:
            return response.json()

# Function to fetch a GitHub user's repositories
def fetch_user_repos(username):
    url = f'https://api.github.com/users/{username}/repos'
    return api_request_with_rate_limit(url)

# Function to assess repository complexity using Google Generative AI
def assess_repository(repo):
    repo_name = repo['name']
    repo_url = repo['html_url']
    readme_url = f"{repo_url}/blob/master/README.md"

    readme_response = requests.get(readme_url)
    readme_content = ''
    if readme_response.status_code == 200:
        readme_content = readme_response.text

    gpt_input = f"Assess the complexity of repository {repo_name}. {readme_content}"
    result = chat.invoke([{"role": "user", "content": gpt_input}])
    gpt_response = result.content

    match = re.search(r"complexity score: ([0-9.]+)", gpt_response)
    if match:
        complexity_score = float(match.group(1))
    else:
        raise ValueError(f"Could not extract complexity score from response: {gpt_response}")

    # Placeholder for LangChain analysis (assuming a custom function `extract_metrics_from_github_repo`).
    code_metrics = extract_metrics_from_github_repo(repo_url)  # Define this function elsewhere
    overall_score = complexity_score + code_metrics.complexity_score

    return repo_name, repo_url, overall_score

# Function to find the most technically challenging repository
def find_most_challenging_repository(username):
    try:
        # Fetch user repositories
        repositories = fetch_user_repos(username)

        if not repositories:
            raise Exception(f"No repositories found for user {username}")

        # Assess complexity for each repository
        repository_scores = []
        for repo in repositories:
            repo_name, repo_url, overall_score = assess_repository(repo)
            repository_scores.append((repo_name, repo_url, overall_score))

        # Sort repositories by score in descending order
        repository_scores.sort(key=lambda x: x[2], reverse=True)

        # Return the most challenging repository
        return repository_scores[0]

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Streamlit app
def main():
    st.title("GitHub Repository Complexity Analysis")

    username = st.text_input("Enter GitHub Username:")

    if st.button("Analyze"):
        if not username:
            st.error("Please enter a GitHub username.")
        else:
            result = find_most_challenging_repository(username)
            if result:
                st.success("Most challenging repository found!")
                st.write(f"Repository Name: {result[0]}")
                st.write(f"Repository URL: {result[1]}")
                st.write(f"Overall Complexity Score: {result[2]}")
            else:
                st.error("Could not find a repository or an error occurred.")

if __name__ == '__main__':
    main()
