import streamlit as st
import advertools as adv
import pandas as pd
import openai

st.markdown(
    """"
    ## 👉🏼 Descrizione
    Questo strumento Streamlit automatizza la generazione di meta descrizioni e titoli SEO-friendly per le pagine del sito web. Utilizzando l'API GPT-3.5 di OpenAI, fornisce un processo semplificato per creare meta tag concisi, accattivanti e pertinenti. Lo strumento è particolarmente utile per i professionisti SEO e gli amministratori di siti web che desiderano ottimizzare la visibilità del loro sito sui motori di ricerca senza l'ingente sforzo manuale tipicamente coinvolto nella creazione di informazioni meta.
    
    ## 👉🏼 Come funziona
    1. **Ottieni una chiave API da OpenAI**: Visita [OpenAI API](https://openai.com/api/) e segui le istruzioni per registrarti e ottenere la tua chiave API. Questa chiave ti permetterà di utilizzare l'API di GPT-3.5 per generare contenuti.
    2. **Prepara l'URL del tuo sito web**: Assicurati di avere l'URL delle pagine del sito per le quali desideri generare nuove meta descrizioni e titoli.
    3. **Inserisci la chiave API e l'URL nel tool**: Utilizza l'interfaccia utente Streamlit dell'applicazione per inserire la tua chiave API di OpenAI e l'URL del sito web.
    4. **Genera le meta descrizioni e i titoli**: Clicca sul pulsante per avviare la generazione dei meta tag. Lo strumento elaborerà le tue richieste e fornirà nuove meta descrizioni e titoli ottimizzati per SEO.
    5. **Scarica i risultati**: Utilizza il pulsante di download per salvare i risultati generati in un file CSV, che poi potrai utilizzare per aggiornare il tuo sito web.
    """
)

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

website_url = st.text_input('Inserire il dominio da scansionare ed analizzare:', '')

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
    st.error('Inserire una chiave API OpenAI e un URL valido del sito web.')
