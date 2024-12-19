import requests
import openai
import streamlit as st

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets['OPENAI_API_KEY']

# Function to fetch a GitHub user's repositories
def fetch_user_repos(username):
    url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch user repositories. Status code: {response.status_code}")

# Function to assess repository complexity using GPT and LangChain
def assess_repository(repo):
    repo_name = repo['name']
    repo_url = repo['html_url']
    readme_url = f"{repo_url}/blob/master/README.md"

    readme_response = requests.get(readme_url)
    readme_content = ''
    if readme_response.status_code == 200:
        readme_content = readme_response.text

    gpt_input = f"Assess the complexity of repository {repo_name}. {readme_content}"
    gpt_response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=gpt_input,
        max_tokens=100,
        temperature=0.5
    )
    complexity_score = gpt_response.choices[0].score

    # Example placeholder for LangChain metrics
    code_metrics = langchain.extract_metrics_from_github_repo(repo_url)
    overall_score = complexity_score + code_metrics.complexity_score

    return repo_name, repo_url, overall_score

# Function to find the most technically challenging repository
def find_most_challenging_repository(username):
    try:
        repositories = fetch_user_repos(username)
        if not repositories:
            raise Exception(f"No repositories found for user {username}")

        repository_scores = []
        for repo in repositories:
            repo_name, repo_url, overall_score = assess_repository(repo)
            repository_scores.append((repo_name, repo_url, overall_score))

        repository_scores.sort(key=lambda x: x[2], reverse=True)
        return repository_scores[0]

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Streamlit app
def app():
    st.title("GitHub Repository Complexity Assessor")
    
    username = st.text_input("Enter GitHub Username:")
    if username:
        st.write(f"Fetching repositories for user: {username}...")
        most_challenging_repo = find_most_challenging_repository(username)
        if most_challenging_repo:
            st.success(f"The most challenging repository for user {username} is:")
            st.write(f"Name: {most_challenging_repo[0]}")
            st.write(f"URL: {most_challenging_repo[1]}")
        else:
            st.write(f"No challenging repositories found for user {username}.")

# Run the Streamlit app
if __name__ == "__main__":
    app()
