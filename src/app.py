import streamlit as st
import pandas as pd
from search_utils import SearchHandler
from llm_utils import LLMHandler
from sheets_utils import SheetsUtils
from config import ERROR_MESSAGES
import time

def initialize_session_state():
    """Initialize session state variables"""
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'current_file_type' not in st.session_state:
        st.session_state.current_file_type = None

def load_data():
    """Handle data loading from CSV or Google Sheets"""
    st.sidebar.title("Data Source")
    source_type = st.sidebar.radio("Choose data source:", ["CSV Upload", "Google Sheets"])
    
    df = None
    if source_type == "CSV Upload":
        uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state.current_file_type = "csv"
            
    else:
        sheets_handler = SheetsUtils()
        sheet_id = st.sidebar.text_input("Enter Google Sheet ID")
        sheet_range = st.sidebar.text_input("Enter Sheet Range (e.g., Sheet1!A1:D10)")
        
        if sheet_id and sheet_range:
            df = sheets_handler.read_sheet(sheet_id, sheet_range)
            if df is not None:
                st.session_state.current_file_type = "sheets"
                st.session_state.sheet_id = sheet_id
                st.session_state.sheet_range = sheet_range
                
    return df

def process_data(df, column_name, prompt):
    """Process data with search and LLM extraction"""
    search_handler = SearchHandler()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_rows = len(df)
    for index, row in df.iterrows():
        entity = row[column_name]
        if not entity:
            print(f"Skipping empty entity at index {index}: {entity}")
            continue
        
        status_text.text(f"Processing {entity}...")
        
        try:
            # Perform search
            search_results = search_handler.search(entity, prompt)
            
            llm_handler = LLMHandler()
            extracted_info = llm_handler.extract_information(search_results, prompt)
            
            results.append({
                "Entity": entity,
                "Extracted_Info": extracted_info,
                "Status": "Success"
            })
            
        except Exception as e:
            results.append({
                "Entity": entity,
                "Extracted_Info": str(e),
                "Status": "Failed"
            })
            
        progress_bar.progress((index + 1) / total_rows)
        time.sleep(0.1)  # Prevent rate limiting
        
    return pd.DataFrame(results)

def main():
    st.title("FetchAI: Information Retrieval Agent")
    initialize_session_state()
    
    # Load data
    df = load_data()
    
    if df is not None:
        st.write("Data Preview:")
        st.write(df.head())
        
        # Column selection
        columns = df.columns.tolist()
        selected_column = st.selectbox("Select entity column:", columns)
        
        # Prompt input
        prompt = st.text_input(
            "Enter search prompt:",
            help="Use {entity_column} as placeholder for entity name"
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            batch_size = st.slider("Batch Size", 1, 50, 10)
            retry_attempts = st.slider("Retry Attempts", 1, 5, 3)
        
        if st.button("Process Data"):
            with st.spinner("Processing..."):
                results_df = process_data(df, selected_column, prompt)
                st.session_state.processed_data = results_df
                
                st.write("Results:")
                st.write(results_df)
                
                # Download options
                st.download_button(
                    "Download Results (CSV)",
                    results_df.to_csv(index=False),
                    "results.csv",
                    "text/csv"
                )
                
                # Write back to Google Sheets if applicable
                if st.session_state.current_file_type == "sheets":
                    if st.button("Update Google Sheet with Results"):
                        sheets_handler = SheetsUtils()
                        success = sheets_handler.write_results(
                            st.session_state.sheet_id,
                            f"{st.session_state.sheet_range}!Next",
                            results_df
                        )
                        if success:
                            st.success("Results written to Google Sheet!")
                        else:
                            st.error("Failed to write to Google Sheet")

if __name__ == "__main__":
    main()