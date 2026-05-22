import os
import pandas as pd

def get_latest_file(input_folder):
    files = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.endswith(".csv")
    ]

    if not files:
        raise FileNotFoundError("No CSV files found in input_data folder.")

    latest_file = max(files, key=os.path.getmtime)
    return latest_file


def load_data(file_path):
    df = pd.read_csv(file_path)
    print(f"Loaded file: {file_path}")
    return df