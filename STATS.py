import streamlit as st
import pandas as pd
from io import BytesIO

# Predefined diagnosis categories and ranges
diagnosis_ranges = {
    "Certain infectious or parasitic diseases": ("1A00", "1H0Z"),
    "Neoplasms": ("2A00", "2F9Z"),
    "Diseases of the blood or blood-forming organs": ("3A00", "3C0Z"),
    "Diseases of the immune system": ("4A00", "4B4Z"),
    "Endocrine, nutritional or metabolic diseases": ("5A00", "5D46"),
    "Mental, behavioral and neurodevelopmental disorders": ("6A00", "6E8Z"),
    "Sleep-wake disorders": ("7A00", "7B2Z"),
    "Diseases of the nervous system": ("8A00", "8E7Z"),
    "Diseases of the visual system": ("9A00", "9E1Z"),
    "Diseases of the ear or mastoid process": ("AA00", "AC0Z"),
    "Diseases of the circulatory system": ("BA00", "BE2Z"),
    "Diseases of the respiratory system": ("CA00", "CB7Z"),
    "Diseases of the digestive system": ("DA00", "DE2Z"),
    "Diseases of the skin": ("EA00", "EM0Z"),
    "Diseases of the musculoskeletal system or connective tissue": ("FA00", "FC0Z"),
    "Diseases of genitourinary system": ("GA00", "GC8Z"),
    "Conditions related to sexual health": ("HA00", "HA8Z"),
    "Pregnancy, childbirth or puerperium": ("JA00", "JB6Z"),
    "Certain conditions originating in perinatal period": ("KA00", "KD5Z"),
    "Developmental anomalies": ("LA00", "LD9Z"),
    "Symptoms, signs or clinical findings not elsewhere classified": ("MA00", "MH2Y"),
    "Injury, poisoning or certain consequences of external causes": ("NA00", "NF2Z"),
    "External causes of morbidity or mortality": ("PA00", "PL2Z"),
    "Factors influencing health status or contact with health services": ("QA00", "QF4Z"),
    "Codes for special purposes": ("RA00", "RA26"),
    "Traditional medicine conditions": ("SA00", "ST2Z"),
    "Functioning assessment": ("VA00", "VC50"),
    "Extension codes": ("XA0060", "XY9U"),
}

def filter_by_diagnosis(df, start_code, end_code):
    return df[df["Diagnosis"].astype(str).apply(lambda x: start_code <= x <= end_code)]

def main():
    st.title("🩺 Diagnosis Code Analyzer")

    uploaded_file = st.file_uploader("📁 Upload diagnosis data (.xlsx, .csv, .txt)", type=["xlsx", "csv", "txt"])

    if uploaded_file:
        # Detect file type and load
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, dtype=str)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, dtype=str)
            else:
                content = uploaded_file.read().decode('utf-8')
                diagnoses = [line.strip() for line in content.splitlines() if line.strip()]
                df = pd.DataFrame(diagnoses, columns=["diagnosis"])
            st.success(f"✅ Loaded {len(df)} records from {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return

        # Normalize columns
        if "diagnosis" in df.columns:
            df[["code", "description"]] = df["diagnosis"].str.split("-", n=1, expand=True)
        elif "Diagnosis" in df.columns:
            df.rename(columns={"Diagnosis": "diagnosis"}, inplace=True)
            df[["code", "description"]] = df["diagnosis"].str.split("-", n=1, expand=True)
        else:
            df.columns = ["diagnosis"]
            df[["code", "description"]] = df["diagnosis"].str.split("-", n=1, expand=True)

        # Diagnosis code analysis
        st.subheader("🔍 Analyze by Diagnosis Code")
        code_input = st.text_input("Enter a diagnosis code (e.g., 8A68.Z):").strip().upper()
        if st.button("Analyze Code") and code_input:
            starts_with = df[df["code"].str.startswith(code_input)]
            exact_match = df[df["code"] == code_input]
            st.info(f"Total diagnoses: {len(df)}")
            st.write(f"Starts with '{code_input}': {len(starts_with)}")
            st.write(f"Exact matches: {len(exact_match)}")
            if not starts_with.empty:
                st.subheader("📄 Matching Diagnoses")
                for code, desc in starts_with[["code", "description"]].drop_duplicates().values:
                    count = len(df[df["code"] == code])
                    percent = (count / len(df)) * 100
                    st.markdown(f"**{code}**: {desc} — Count: {count} ({percent:.2f}%)")

            st.subheader("📊 Top 10 Most Frequent Diagnosis Codes")
            st.dataframe(df["code"].value_counts().head(10).rename("Count"))

        # Range filtering
        st.subheader("🗂️ Filter by Diagnosis Code Range")
        col1, col2 = st.columns(2)
        with col1:
            start_code = st.text_input("Start code (e.g., 1A00)").strip().upper()
        with col2:
            end_code = st.text_input("End code (e.g., 1H0Z)").strip().upper()

        if st.button("Filter by Range") and start_code and end_code:
            category_name = None
            for category, (start, end) in diagnosis_ranges.items():
                if start_code >= start and end_code <= end:
                    category_name = category
                    break

            filtered_df = filter_by_diagnosis(df, start_code, end_code)

            if category_name:
                st.success(f"📘 Category: {category_name}")
            else:
                st.warning("⚠️ Range does not match any predefined category.")

            st.write(f"Number of matching diagnoses: {len(filtered_df)}")
            st.dataframe(filtered_df)

            # Download CSV
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Filtered Data", csv, "filtered_diagnoses.csv", "text/csv")

if __name__ == "__main__":
    main()
