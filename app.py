from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st

def getData(userName):
    url = "https://github.com/{}?tab=repositories".format(userName)
    page = requests.get(url)
    soup = BeautifulSoup(page.content , 'html.parser')
    info = {}

    # Scraping Profile Info

    #full Name
    info['name'] = soup.find(class_ = 'vcard-fullname').get_text()
    #image
    info['image_url'] =  soup.find(class_ = 'avatar-user')['src']
    #followers and follwoing
    info['followers'] = soup.select_one("a[href*=followers]").get_text().strip().split('\n')[0]
    info['following'] = soup.select_one("a[href*=following]").get_text().strip().split('\n')[0]
    
    #location
    try:
        info['location'] = soup.select_one('li[itemprop*=home]').get_text().strip()
    except:
        info['location'] = ''
    #url
    try:
        info['url'] = soup.select_one('li[itemprop*=url]').get_text().strip()
    except:
        info['url'] = ''
    
    #get Repositories as a dataframe
    repos = soup.find_all(class_ = 'source')
    repo_info = []
    for repo in repos:

        #repo name and link
        try:
            name = repo.select_one('a[itemprop*=codeRepository]').get_text().strip()
            link = 'https://github.com/{}/{}'.format(userName,name)
        except:
            name = ''
            link = ''
        
        #repo update time
        try:
            updated = repo.find('relative-time').get_text()
        except:
            updated = ''
        
        # programming language
        try:
            language = repo.select_one('span[itemprop*=programmingLanguage]').get_text()
        except:
            language = ''
        
        # description
        try:
            description = repo.select_one('p[itemprop*=description]').get_text().strip()
        except:
            description = ''
        
        repo_info.append({'name': name ,
        'link': link , 
        'updated ':updated , 
        'language': language , 
        'description':description})
    repo_info = pd.DataFrame(repo_info)
    return info , repo_info
st.title("Github Scraper")

userName = st.text_input('Enter Github Username')

if userName != '':
    try:
        info, repo_info = getData(userName)

        for key , value in info.items():
            if key != 'image_url':
                st.subheader(
                    '''
                    {} : {} 
                    '''.format(key, value)
                )
            else:
                st.image(value)
        st.subheader(" Recent Repositories")
        st.table(repo_info)
    except:
        st.subheader("User doesn't exist")

