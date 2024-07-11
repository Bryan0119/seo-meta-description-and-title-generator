import streamlit as st
import advertools as adv
import pandas as pd
from openai import OpenAI
import json

def get_seo_suggestions(row, client):
    system_message = "You are an expert SEO consultant tasked with improving website meta descriptions and titles."
    
    prompt_desc = f"""
    Create an optimized meta description for a webpage.
    
    Webpage Title: {row['title']}
    URL: {row['url']}
    Current Meta Description: {row['meta_desc']}
    
    Requirements:
    1. Maximum 155 characters
    2. Include the website name
    3. Include a clear call-to-action
    4. Be concise, engaging, and relevant to the page content
    5. Include important keywords if possible
    
    Respond with a JSON object containing only the new meta description.
    """
    
    prompt_title = f"""
    Create an optimized page title for a webpage.
    
    Current Title: {row['title']}
    URL: {row['url']}
    
    Requirements:
    1. Maximum 60 characters
    2. Include the website name
    3. Be engaging and descriptive
    4. Include important keywords if possible
    
    Respond with a JSON object containing only the new title.
    """
    
    try:
        response_desc = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_desc}
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=100
        )
        new_desc = json.loads(response_desc.choices[0].message.content)["meta_description"]
        
        response_title = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_title}
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=50
        )
        new_title = json.loads(response_title.choices[0].message.content)["title"]
        
        return new_desc, new_title
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None

def crawl_and_analyze_website(website_url, client):
    output_file = 'website_crawl.jl'
    adv.crawl(website_url, output_file, follow_links=True)
    crawl_df = pd.read_json(output_file, lines=True)
    crawl_df = crawl_df.drop_duplicates('url', keep='last').reset_index(drop=True)
    crawl_df = crawl_df.dropna(subset=['title', 'meta_desc'])
    
    results = []
    for _, row in crawl_df.iterrows():
        new_desc, new_title = get_seo_suggestions(row, client)
        if new_desc and new_title:
            results.append({
                'url': row['url'],
                'current_title': row['title'],
                'new_title': new_title,
                'current_meta_desc': row['meta_desc'],
                'new_meta_desc': new_desc
            })
    
    return pd.DataFrame(results)

st.title('Advanced SEO Meta Description and Title Generator (GPT-4)')

st.markdown("""
#### Description
This Streamlit tool automates the generation of SEO-friendly meta descriptions and titles for web pages. 
It uses OpenAI's GPT-4 API to provide high-quality, context-aware suggestions tailored to your website content.

#### How it works
1. **Enter your OpenAI API Key**: You'll need a valid API key from OpenAI with access to GPT-4.
2. **Enter your website URL**: Provide the URL of the site you want to analyze.
3. **Run the analysis**: The tool will crawl your site, analyze the content, and generate optimized meta descriptions and titles.
4. **Review and download results**: You can view the suggestions directly in the app and download them as a CSV file.

#### Note
This tool uses GPT-4, which may incur higher costs than GPT-3.5-turbo. Please be aware of your API usage and associated costs.
""")

st.markdown("---")

openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
website_url = st.text_input('Enter the domain to scan and analyze:', '')

if st.button('Analyze Website') and openai_api_key and website_url:
    client = OpenAI(api_key=openai_api_key)
    with st.spinner('Scanning and analyzing the website... This may take a few minutes.'):
        try:
            results_df = crawl_and_analyze_website(website_url, client)
            st.success("Analysis complete!")
            st.dataframe(results_df)
            
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="seo_results.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
else:
    st.warning('Please enter both an OpenAI API Key and a valid website URL to proceed.')

st.markdown("---")
st.markdown("Built with ❤️ using OpenAI's GPT-4 and Streamlit")
