import pandas as pd
import re
import os

def clean_system_noise(df: pd.DataFrame) -> pd.DataFrame:
    """Dynamically drops columns starting with underscore or named 'Label'"""
    cols_to_drop = [c for c in df.columns if str(c).startswith('_') or c == 'Label']
    return df.drop(columns=cols_to_drop)

def clean_routing_text(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Removes routing text inside parentheses and leading numbers"""
    if column_name in df.columns:
        df[column_name] = df[column_name].astype(str).apply(
            lambda x: re.sub(r'\s*\(.*?\)', '', x)
        ).str.replace(r'^\d+\s+', '', regex=True).str.strip()
    return df

def unpivot_survey_block(df: pd.DataFrame, prefix: str, id_vars: list, value_name: str) -> pd.DataFrame:
    """Dynamically target and melt a specific block of wide-format survey questions"""
    target_cols = [c for c in df.columns if str(c).startswith(prefix)]
    
    melted = pd.melt(
        df, 
        id_vars=id_vars, 
        value_vars=target_cols, 
        var_name=value_name, 
        value_name="Is_Selected"
    )
    
    # Fixed: Corrected pandas boolean indexing and column dropping syntax
    melted = melted[melted["Is_Selected"] == 1].drop(columns=["Is_Selected"])
    
    # Clean the long column headers to extract just the specific answer text after the slash
    melted[value_name] = melted[value_name].apply(
        lambda x: str(x).split('/')[-1].strip() if '/' in str(x) else str(x)
    )
    
    return melted

def execute_pipeline(file_path: str):
    print("Loading enterprise dataset...")
    df = pd.read_excel(file_path, sheet_name="Database Start")
    
    # Rename the long greeting column to act as our primary ID for the relational mapping
    id_col_raw = "Ներկայացեք՝ Բարև Ձեզ, իմ անունը...... է: Ես «Ի-Վի» հետազոտական ընկերությունից եմ..."
    if id_col_raw in df.columns:
        df = df.rename(columns={id_col_raw: "Respondent_ID"})
    
    # Clean up
    df = clean_system_noise(df)
    df = clean_routing_text(df, "A8. Հաճախ եք այցելում այս սպասարկման կենտրոն:")
    
    # Fixed: Provided essential primary keys to carry over during the unpivot
    core_ids = ["Respondent_ID", "Օպերատոր", "Հարցազրուցավար"]
    
    print("Unpivoting S3 Purpose Block...")
    s3_long = unpivot_survey_block(
        df, 
        prefix="S3. Դուք քիչ առաջ այցելել եք", 
        id_vars=core_ids, 
        value_name="Visit_Purpose"
    )
    
    print("Unpivoting 4.5 Nested Details Block...")
    details_long = unpivot_survey_block(
        df, 
        prefix="4.5_", 
        id_vars=core_ids, 
        value_name="Specific_Detail"
    )
    
    # Export clean outputs to the data folder
    os.makedirs("data", exist_ok=True)
    s3_long.to_csv("data/clean_visit_purposes.csv", index=False, encoding='utf-8-sig')
    details_long.to_csv("data/clean_complaint_details.csv", index=False, encoding='utf-8-sig')
    print("✔ Pipeline execution complete. Clean relational tables exported.")

if __name__ == "__main__":
    execute_pipeline("data/csi_database.xlsx")
