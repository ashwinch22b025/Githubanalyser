from setuptools import find_packages, setup
from typing import List

HYPEN_E_DOT = '-e .'

def get_requirements(file_path: str) -> List[str]:
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.strip() for req in requirements if req.strip()]
        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    return requirements

setup(
    name='GithubAutomatedAnalysis',
    version='0.0.1',
    author='Sai Vamsi M.',
    author_email='Vamsisreenivas71054@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt'),
    description='A tool for analyzing GitHub repositories using Google Generative AI and LangChain.',
    long_description=open('README.md').read() if 'README.md' in find_packages() else 'Github Repository Analysis Tool',
    long_description_content_type='text/markdown',
    url='https://github.com/sai-vamsi-m',  # Update with your GitHub project URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3',  # Adjust as per your Python version
)
