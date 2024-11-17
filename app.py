# import streamlit as st
# import pandas as pd
# import requests
# import csv
# from groq import Groq

# st.title("FetchAI: An Agent for Information Retrieval")

# # File uploader
# uploaded_file = st.file_uploader("Choose a CSV File", type="csv")
# if uploaded_file:
#     df = pd.read_csv(uploaded_file)
#     st.write("Data Preview:")
#     st.write(df)

# # Prompt input
# prompt = st.text_input("Enter the query prompt (e.g., 'Get the email for {company}')")

# # Define search function with SerpAPI
# import requests

# def search_company(company_name, prompt):
#     api_key = "389998f6fb262d620b83dcb44ae1d371588bd1b8b98d13e662122630e90cf6a7"  # Replace with your actual SerpAPI key
#     query = prompt.replace("{company}", company_name)
    
#     # Prepare the request parameters
#     params = {
#         "q": query,
#         "api_key": api_key,
#         "engine": "google"  # Specifies the Google search engine
#     }

#     # Make a request to the SerpAPI endpoint
#     response = requests.get("https://serpapi.com/search", params=params)
#     result = response.json()

#     # Return search results if they are available
#     return result.get("organic_results", [])


# # Define LLM extraction function with OpenAI
# def extract_information(results, prompt):
#     if not results:
#         return "No results found."
#     search_text = " ".join([result.get('snippet', '') for result in results])
#      = Groq(api_key="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")
#     response = client.chat.completions.create(
#         model="llama3-8b-8192",
#         messages=[
#             {"role": "system", "content": "You are an assistant that extracts specific information from search results."},
#             {"role": "user", "content": prompt.replace("{search_results}", search_text)}
#         ],
#         temperature=0.5,
#         max_tokens=100
#     )
#     return response.choices[0].message.content.strip()



# # Button to trigger search
# search_button = st.button("Search")
# if search_button and uploaded_file and prompt:
#     extracted_data = []
#     for index, row in df.iterrows():
#         company_name = row["Company"]  # Ensure your CSV has a 'Company' column
#         st.write(f"Searching for {company_name}...")
        
#         # Search and extract
#         search_results = search_company(company_name, prompt)
#         extracted_info = extract_information(search_results, prompt)
        
#         # Display individual results
#         st.write(f"Extracted info for {company_name}: {extracted_info}")
        
#         # Save results for CSV
#         extracted_data.append([company_name, extracted_info])

#     # Display all extracted data in a table
#     extracted_df = pd.DataFrame(extracted_data, columns=["Company", "Extracted Info"])
#     st.write("All Extracted Information:")
#     st.write(extracted_df)

#     # Add download button
#     def download_csv(data, filename="results.csv"):
#         data.to_csv(filename, index=False)
#         with open(filename, "rb") as file:
#             st.download_button("Download Results as CSV", data=file, file_name=filename)

#     # Call download function
#     download_csv(extracted_df)
