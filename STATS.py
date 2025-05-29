import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output
from io import BytesIO

def analyze_diagnosis_data():
    # Create widgets
    upload = widgets.FileUpload(
        accept='.xlsx,.csv,.txt',  # Accepted file types
        multiple=False,
        description='Choose file'
    )
    
    code_input = widgets.Text(
        value='',
        placeholder='e.g. 8A68.Z',
        description='Diagnosis code:',
        disabled=False
    )
    
    analyze_button = widgets.Button(description="Analyze")
    output = widgets.Output()
    
    def on_analyze_button_clicked(b):
        with output:
            output.clear_output()
            code_value = code_input.value.strip().upper()
            
            if not upload.value:
                print("Please upload a file first")
                return
            if not code_value:
                print("Please enter a diagnosis code")
                return
                
            try:
                # Get uploaded file - handle the tuple structure correctly
                uploaded_file = upload.value[0]  # Get first (and only) uploaded file
                file_content = uploaded_file['content']
                file_name = uploaded_file['name']
                
                # Read file based on extension
                if file_name.endswith('.xlsx'):
                    df = pd.read_excel(BytesIO(file_content))
                    print(f"Successfully read Excel file with {len(df)} records")
                elif file_name.endswith('.csv'):
                    df = pd.read_csv(BytesIO(file_content))
                    print(f"Successfully read CSV file with {len(df)} records")
                else:  # Assume text file
                    text_content = file_content.decode('utf-8')
                    diagnoses = [line.strip() for line in text_content.split('\n') if line.strip()]
                    df = pd.DataFrame(diagnoses, columns=['diagnosis'])
                    print(f"Successfully read text file with {len(df)} records")
                
                # If file has multiple columns, assume first column contains diagnoses
                if len(df.columns) > 1:
                    diagnosis_col = df.columns[0]
                    df = df[[diagnosis_col]].copy()
                    df.columns = ['diagnosis']
                
                # Split code and description
                df[['code', 'description']] = df['diagnosis'].str.split('-', n=1, expand=True)
                
                # Count occurrences
                count = len(df[df['code'].str.startswith(code_value)])
                exact_count = len(df[df['code'] == code_value])
                matches = df[df['code'].str.startswith(code_value)]
                
                # Display results
                print("\n=== Analysis Results ===")
                print(f"File: {file_name}")
                print(f"Diagnosis code: {code_value}")
                print(f"Total records in dataset: {len(df)}")
                print(f"\nCount of diagnoses starting with '{code_value}': {count}")
                print(f"Exact matches for '{code_value}': {exact_count}")
                
                if count > 0:
                    print("\nMatching diagnoses found:")
                    for code, desc in matches[['code', 'description']].drop_duplicates().values:
                        cnt = len(df[df['code'] == code])
                        print(f"\n{code}: {desc}")
                        print(f"  Count: {cnt}")
                        print(f"  Percentage of total: {(cnt/len(df)*100):.2f}%")
                
                # Show top 10 most frequent diagnoses
                top_10 = df['code'].value_counts().head(10)
                print("\nTop 10 most frequent diagnoses in dataset:")
                display(top_10)
                
            except Exception as e:
                print(f"Error: {str(e)}")
                print("\nPlease check your file format. Supported formats:")
                print("- Excel (.xlsx) with diagnosis codes in first column")
                print("- CSV file with diagnosis codes in format 'CODE-Description'")
                print("- Text file with one diagnosis per line in format 'CODE-Description'")
    
    analyze_button.on_click(on_analyze_button_clicked)
    
    # Display the widgets
    display(widgets.VBox([
        widgets.HTML("<h3>Diagnosis Code Analyzer</h3>"),
        widgets.HTML("Upload your dataset file (.xlsx, .csv, or .txt):"),
        upload,
        widgets.HTML("Enter a diagnosis code to analyze:"),
        code_input,
        analyze_button,
        output
    ]))

# Run the analyzer
analyze_diagnosis_data()
