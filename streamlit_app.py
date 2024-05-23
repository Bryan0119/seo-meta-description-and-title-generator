import streamlit as st
import advertools as adv
import pandas as pd
import openai

def get_seo_suggestions(row, api_key):
    openai.api_key = api_key
    
    # Generazione della nuova descrizione
    prompt_desc = (
        f"Ho bisogno di aiuto per scrivere una meta descrizione per un sito web. Il tuo ruolo è quello di agente SEO. Il titolo del sito web è '{row['title']}'. "
        f"L'URL del sito web è '{row['url']}'. "
        f"La descrizione meta esistente è '{row['meta_desc']}'. "
        f"Per favore scrivi una nuova meta descrizione che sia più concisa, accattivante e pertinente al contenuto del sito web. "
        f"Assicurati di includere il nome del sito web e una call to action."
    )
    
    response_desc = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt_desc,
        max_tokens=150
    )
    new_desc = response_desc.choices[0].text.strip()
    
    # Generazione del nuovo titolo
    prompt_title = (
        f"Ho bisogno di aiuto per scrivere un nuovo titolo per un sito web. Il tuo ruolo è quello di agente SEO. Il titolo attuale è '{row['title']}'. "
        f"L'URL del sito web è '{row['url']}'. Per favore scrivi un nuovo titolo che sia accattivante, "
        f"conciso e includa parole chiave pertinenti al contenuto del sito web."
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
st.title('Generatore di Meta Descrizioni e Titoli SEO')

st.markdown("""
#### Descrizione
Questo strumento Streamlit è progettato per automatizzare la generazione di meta descrizioni e titoli SEO-friendly per le pagine del sito web. Utilizzando l'API GPT-3.5 di OpenAI, fornisce un processo semplificato per creare meta tag concisi, accattivanti e pertinenti. Lo strumento è particolarmente utile per i professionisti SEO e gli amministratori di siti web che desiderano ottimizzare la visibilità del loro sito sui motori di ricerca senza l'ingente sforzo manuale tipicamente coinvolto nella creazione di informazioni meta.

#### Come funziona
1. **Ottieni una chiave API da OpenAI**: Visita [OpenAI API](https://platform.openai.com/api-keys) e segui le istruzioni per registrarti e ottenere la tua chiave API. Questa chiave ti permetterà di utilizzare l'API di GPT-3.5 per generare contenuti.
2. **Prepara l'URL del tuo sito web**: Assicurati di avere l'URL delle pagine del sito per le quali desideri generare nuove meta descrizioni e titoli.
3. **Inserisci la chiave API e l'URL nel tool**: Utilizza l'interfaccia utente Streamlit dell'applicazione per inserire la tua chiave API di OpenAI e l'URL del sito web.
""")

st.markdown("---")

openai_api_key = st.text_input("Inserisci la tua chiave API di OpenAI:", type="password")

website_url = st.text_input('Inserire il dominio da scansionare ed analizzare:', '')

if st.button('Analizza il Sito Web') and openai_api_key and website_url:
    with st.spinner('Scansione e analisi del sito web in corso...'):
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
