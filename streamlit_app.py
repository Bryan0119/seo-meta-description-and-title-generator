import streamlit as st
import advertools as adv
import pandas as pd
import openai

def get_seo_suggestions(row, api_key):
    openai.api_key = api_key
    
    # Generazione della nuova descrizione
    prompt_desc = (
        f"I need help writing a meta description for a website. Your role is SEO agent. The title of the website is '{row['title']}'. "
        f"The URL of the website is '{row['url']}'. "
        f"The existing meta description is '{row['meta_desc']}'. "
        f"Please write a new meta description that is more concise, compelling, and relevant to the website's content. "
        f"Make sure to include the website's name and a call to action."
    )
    
    response_desc = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt_desc,
        max_tokens=150
    )
    new_desc = response_desc.choices[0].text.strip()
    
    # Generazione del nuovo titolo
    prompt_title = (
        f"I need help writing a new title for a website. Your role is SEO agent. The current title is '{row['title']}'. "
        f"The URL of the website is '{row['url']}'. Please write a new title that is catchy, "
        f"concise, and includes keywords relevant to the website's content."
    )
    
    response_title = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt_title,
        max_tokens=60
    )
    new_title = response_title.choices[0].text.strip()
    
    return new_desc, new_title

def crawl_and_analyze_website(website_url, api_key):
    output_file = 'website_crawl.jl'
    adv.crawl(website_url, output_file, follow_links=True)
    crawl_df = pd.read_json(output_file, lines=True)
    crawl_df = crawl_df.drop_duplicates('url', keep='last').reset_index(drop=True)
    crawl_df = crawl_df.dropna(subset=['title', 'meta_desc'])
    
    # Applica la funzione per generare nuove descrizioni e titoli
    crawl_df[['new_meta_desc', 'new_title']] = crawl_df.apply(lambda row: get_seo_suggestions(row, api_key), axis=1, result_type='expand')
    return crawl_df[['title', 'new_title', 'url', 'meta_desc', 'new_meta_desc']]

# Interfaccia utente Streamlit
st.title('SEO Meta Description and Title Generator')

openai_api_key = st.text_input("Inserisci la tua chiave API di OpenAI:", type="password")

website_url = st.text_input('Enter the website URL to crawl and analyze:', '')

if st.button('Analyze Website') and openai_api_key and website_url:
    with st.spinner('Crawling and analyzing website...'):
        results_df = crawl_and_analyze_website(website_url, openai_api_key)
        st.dataframe(results_df)
        
        # Converti il DataFrame in una stringa CSV
        csv = results_df.to_csv(index=False).encode('utf-8')
        
        # Crea un pulsante di download per il CSV
        st.download_button(
            label="Scarica i risultati come CSV",
            data=csv,
            file_name="risultati_seo.csv",
            mime="text/csv",
        )
else:
    st.error('Please enter both an OpenAI API key and a valid website URL.')
