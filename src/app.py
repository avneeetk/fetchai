import streamlit as st
import pandas as pd
from search_utils import SearchHandler
from llm_utils import LLMHandler
from sheets_utils import SheetsUtils
from config import ERROR_MESSAGES
import logging

def initialize_session_state():
    """Initialize session state variables"""
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'current_file_type' not in st.session_state:
        st.session_state.current_file_type = None

def load_data():
    """Handle data loading from CSV or Google Sheets"""
    st.header("Data Source")
    source_type = st.radio("Choose data source:", ["CSV Upload", "Google Sheets"])

    df = None
    if source_type == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV file", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state.current_file_type = "csv"
    else:
        # Google Sheets input
        sheets_handler = SheetsUtils()
    
        # URL input
        sheet_url = st.text_input("Enter Google Sheet URL")
        if sheet_url:
            try:
                sheet_id = SheetsUtils.get_sheet_id_from_url(sheet_url)
                st.session_state.sheet_id = sheet_id
                st.success("Valid Google Sheet URL!")
                
                sheet_range = st.text_input(
                    "Enter Sheet Name and Range (e.g., Sheet1!A1:D10)",
                    help="Specify the range of data to load."
                )
                if sheet_range:
                    df = sheets_handler.read_sheet(sheet_id, sheet_range)
                    if not df.empty:
                        st.session_state.current_file_type = "sheets"
                        st.session_state.sheet_range = sheet_range
                    else:
                        st.error("Failed to load data. Check your range or sheet permissions.")
            except ValueError as e:
                st.error(str(e))
                
    return df


def process_data(df, column_name, prompt):
    """Process data with search and LLM extraction."""
    search_handler = SearchHandler()  # Pass SERPAPI_KEY implicitly
    llm_handler = LLMHandler()
    results = []

    progress_bar = st.progress(0)
    status_text = st.empty()
    total_rows = len(df)

    for index, row in df.iterrows():
        entity = row[column_name]
        if not entity:
            logging.warning(f"Skipping empty entity at index {index}")
            continue

        status_text.text(f"Processing {entity} ({index + 1}/{total_rows})...")

        try:
            # Replace placeholder with the current entity
            search_prompt = prompt.replace("{entity}", entity)

            # Perform search
            search_results = search_handler.search(entity, prompt)

            # Verify search results
            if search_results["status"] == "error":
                raise ValueError(search_results.get("message", "Search error occurred."))
            if search_results["status"] == "no_results" or not search_results["data"]:
                raise ValueError(f"No relevant search snippets for {entity}")

            # Filter search snippets for relevance
            search_text = " ".join([
                result.get("snippet", "")
                for result in search_results["data"]
                if entity.lower() in result.get("snippet", "").lower()
            ])
            if not search_text:
                raise ValueError(f"No relevant search snippets for {entity}")

            logging.info(f"Search text for {entity}: {search_text}")

            # Generate prompt for LLM
            entity_prompt = f"{prompt.replace('{entity}', entity)}\n\nSearch Results:\n{search_text}"
            extracted_info = llm_handler.extract_information(search_results, entity_prompt)

            # Extract and validate LLM output
            if isinstance(extracted_info, dict):
                extracted_text = extracted_info.get("data", "No relevant data found.")
            else:
                extracted_text = str(extracted_info)

            if entity.lower() not in extracted_text.lower():
                raise ValueError(f"Extracted information does not match entity: {extracted_text}")

            # Append the plain-text result
            results.append({
                "Entity": entity,
                "Extracted Info": extracted_text,
                "Status": "Success"
            })

        except Exception as e:
            # Append error in plain-text format
            results.append({
                "Entity": entity,
                "Extracted Info": str(e),
                "Status": "Failed"
            })

        # Update progress bar
        progress_bar.progress((index + 1) / total_rows)

    results_df = pd.DataFrame(results)
    return results_df



def main():
    st.title("FetchAI: Information Retrieval Agent")
    initialize_session_state()

    # Load data
    df = load_data()

    if df is not None:
        st.write("Data Preview:")
        st.dataframe(df)

        columns = df.columns.tolist()
        selected_column = st.selectbox("Select entity column:", columns)

        prompt = st.text_input(
            "Enter search prompt:",
            help="Use {entity} as placeholder for the entity name (e.g., 'Find latest news about {entity}')"
        )

        if st.button("Process Data"):
            if not prompt:
                st.error("Please include {entity} in your prompt")
                return

            with st.spinner("Processing..."):
                results_df = process_data(df, selected_column, prompt)
                st.session_state.processed_data = results_df

                st.write("Results:")
                st.dataframe(results_df)

                st.download_button(
                    "Download Results (CSV)",
                    results_df.to_csv(index=False),
                    "results.csv",
                    "text/csv"
                )

if __name__ == "__main__":
    main()


