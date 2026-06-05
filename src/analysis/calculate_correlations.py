import pandas as pd
import os

def rename_survey_columns(df):
    new_names = {}
    for col in df.columns:
        if col.startswith("A2."): new_names[col] = "A2"
        elif col.startswith("A3."): new_names[col] = "A3"
        elif col.startswith("A4."): new_names[col] = "A4"
        elif col.startswith("5."):
            # Fixed: Extract the first part of the string (e.g., "5.1")
            short_code = col.split(" ")[0]  
            new_names[col] = f"A{short_code}" 
        elif col.startswith("S1.") or col == "Օպերատոր":
            # Fixed: Dynamically renames either S1 or the Armenian column header
            new_names[col] = "Operator" 
            
    return df.rename(columns=new_names)

def generate_csi_correlations(file_path, sheet_name):
    # 1. Ingestion
    print("Loading raw satisfaction data...")
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found. Please run the generation script first.")
        return

    # 2. Rename columns to standardized codes
    df = rename_survey_columns(df)
    
    # Ensure scoring columns are numeric before doing math
    score_cols = ['A2', 'A3', 'A4'] + [f"A5.{i}" for i in range(1, 13)]
    for col in score_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 3. Induce the 'Average' metric column
    df['Average'] = (df['A2'] + df['A3'] + df['A4']) / 3

    # Define correlation matrix targets
    corr_cols = [
        'Average', 'A5.1', 'A5.2', 'A5.3', 'A5.4', 'A5.5', 'A5.6', 
        'A5.7', 'A5.8', 'A5.9', 'A5.10', 'A5.11', 'A5.12'
    ]

    # Filter available columns just in case some are missing
    available_corr_cols = [c for c in corr_cols if c in df.columns]

    # 4. Compute Operator-Specific Correlation Matrices via Kendall's Tau
    print("Computing Kendall correlations...")
    oper_col = 'Operator'
    
    if oper_col not in df.columns:
        print("Error: 'Operator' column not found. Check the column renaming logic.")
        return

    # Fixed: Matched the exact strings from the mock dataset generator
    corr_v = df.loc[df[oper_col] == 'Viva', available_corr_cols].corr(method='kendall').round(3)
    corr_t = df.loc[df[oper_col] == 'Team Telecom', available_corr_cols].corr(method='kendall').round(3)
    corr_u = df.loc[df[oper_col] == 'Ucom', available_corr_cols].corr(method='kendall').round(3)

    # Reset index to retain variable labels in the final spreadsheet
    corr_v = corr_v.reset_index().rename(columns={'index': 'Correlation'})
    corr_t = corr_t.reset_index().rename(columns={'index': 'Correlation'})
    corr_u = corr_u.reset_index().rename(columns={'index': 'Correlation'})

    # 5. Export to a single multi-sheet workbook
    os.makedirs("data", exist_ok=True)
    output_file = 'data/Operator_Correlations_Output.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        corr_v.to_excel(writer, sheet_name='viva_corr', index=False)
        corr_t.to_excel(writer, sheet_name='team_corr', index=False)
        corr_u.to_excel(writer, sheet_name='ucom_corr', index=False)

    print(f"✔ Pipeline execution complete. Matrices exported to {output_file}.")

if __name__ == "__main__":
    generate_csi_correlations(
        file_path='data/csi_database.xlsx', 
        sheet_name='Database Start'
    )
