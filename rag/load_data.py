import pandas as pd

def load_courses(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    
    # Standardize column names
    df.columns = [column.strip().lower().replace(" ", "_") for column in df.columns]
    
    # Remove completely empty rows
    df = df.dropna(how="all")
    
    # Remove duplicate courses
    df = df.drop_duplicates(subset=["course_name"])
    
    # Fill missing text fields
    text_columns = [
        "course_name",
        "university",
        "difficulty_level",
        "course_description",
        "skills",
        "course_url"
    ]
    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].fillna("").astype(str).str.strip()
            
    # Coerce rating to float
    df["course_rating"] = pd.to_numeric(df["course_rating"], errors="coerce").fillna(0.0)
    
    # Reset index and insert 1-based unique course_id
    df = df.reset_index(drop=True)
    df.insert(0, "course_id", range(1, len(df) + 1))
    
    return df
