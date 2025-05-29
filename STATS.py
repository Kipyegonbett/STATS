import streamlit as st
import pandas as pd
from io import BytesIO

def analyze_diagnosis_data(uploaded_file, code_value):
    if uploaded_file is None:
        st.error("Please upload a file first")
        return
    if not code_value:
        st.error("Please enter a diagnosis code")
        return

    try:
        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()

        # Read file based on extension
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file_content))
            st.success(f"Successfully read Excel file with {len(df)} records")
        elif file_name.endswith('.csv'):
            df = pd.read_csv(BytesIO(file_content))
            st.success(f"Successfully read CSV file with {len(df)} records")
        else:  # Assume text file
            text_content = file_content.decode('utf-8')
            diagnoses = [line.strip() for line in text_content.split('\n') if line.strip()]
            df = pd.DataFrame(diagnoses, columns=['diagnosis'])
            st.success(f"Successfully read text file with {len(df)} records")

        # Process Data
        if len(df.columns) > 1:
            diagnosis_col = df.columns[0]
            df = df[[diagnosis_col]].copy()
            df.columns = ['diagnosis']

        df[['code', 'description']] = df['diagnosis'].str.split('-', n=1, expand=True)

        # Filter by code
        count = len(df[df['code'].str.startswith(code_value)])
        exact_count = len(df[df['code'] == code_value])
        matches = df[df['code'].str.startswith(code_value)]

        # Display results
        st.subheader("Analysis Results")
        st.write(f"File: {file_name}")
        st.write(f"Diagnosis code: {code_value}")
        st.write(f"Total records in dataset: {len(df)}")
        st.write(f"\nCount of diagnoses starting with '{code_value}': {count}")
        st.write(f"Exact matches for '{code_value}': {exact_count}")

        if count > 0:
            st.subheader("Matching Diagnoses Found")
            for code, desc in matches[['code', 'description']].drop_duplicates().values:
                cnt = len(df[df['code'] == code])
                st.write(f"\n**{code}:** {desc}")
                st.write(f"  **Count:** {cnt}")
                st.write(f"  **Percentage of total:** {(cnt/len(df)*100):.2f}%")

        # Show top 10 diagnoses
        top_10 = df['code'].value_counts().head(10)
        st.subheader("Top 10 Most Frequent Diagnoses in Dataset")
        st.write(top_10)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.warning("Please check your file format. Supported formats:")
        st.write("- Excel (.xlsx) with diagnosis codes in first column")
        st.write("- CSV file with diagnosis codes in format 'CODE-Description'")
        st.write("- Text file with one diagnosis per line in format 'CODE-Description'")

# Streamlit UI
st.title("Diagnosis Code Analyzer")
uploaded_file = st.file_uploader("Upload your dataset file (.xlsx, .csv, or .txt)", type=["xlsx", "csv", "txt"])
code_value = st.text_input("Enter a diagnosis code:", "").strip().upper()

if st.button("Analyze"):
    analyze_diagnosis_data(uploaded_file, code_value)
