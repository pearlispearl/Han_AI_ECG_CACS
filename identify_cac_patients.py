#!/usr/bin/env python3
"""
Identify patients with CAC scores from output.csv
This script analyzes the output.csv file to find which patients have CAC scores included.

Usage:
    python identify_cac_patients.py
"""

import pandas as pd
import os

def identify_patients_with_cac_scores():
    """
    Identify patients with CAC scores from output.csv
    """
    # Path to output.csv
    csv_path = "/home/mirulab02/ekg-rama/output.csv"
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} records from {csv_path}")
        
        # Look for CAC score columns (assuming they exist in the data)
        # Common column names for CAC scores
        cac_columns = ['score', 'CAC_score', 'calcium_score', 'coronary_calcification']
        
        # Find which columns contain CAC score information
        found_cac_columns = []
        for col in df.columns:
            if any(cac_col.lower() in col.lower() for cac_col in cac_columns):
                found_cac_columns.append(col)
        
        print(f"Found potential CAC score columns: {found_cac_columns}")
        
        # Identify patients with CAC scores (non-null values)
        patients_with_scores = []
        patients_without_scores = []
        
        # If we have a patient ID column, use it
        id_columns = ['HN', 'Patient_ID', 'patient_id', 'hn']
        id_column = None
        
        for col in df.columns:
            if any(id_col.lower() in col.lower() for id_col in id_columns):
                id_column = col
                break
                
        if id_column is None:
            # Try to find a column that looks like patient ID
            for col in df.columns:
                if 'hn' in col.lower() or 'patient' in col.lower():
                    id_column = col
                    break
        
        if id_column is None:
            print("Warning: No patient ID column found. Using row indices.")
            id_column = "row_index"
            
        # Process each row to determine if it has a CAC score
        for index, row in df.iterrows():
            has_score = False
            
            # Check all potential CAC columns
            for col in found_cac_columns:
                if pd.notna(row[col]) and str(row[col]).strip() != '':
                    has_score = True
                    break
            
            # Get patient ID
            patient_id = row.get(id_column, f"Unknown_{index}")
            
            if has_score:
                patients_with_scores.append({
                    'patient_id': patient_id,
                    'score_value': row.get(found_cac_columns[0], None) if found_cac_columns else None
                })
            else:
                patients_without_scores.append(patient_id)
        
        # Display results
        print(f"\n=== CAC Score Analysis ===")
        print(f"Total records: {len(df)}")
        print(f"Patients with CAC scores: {len(patients_with_scores)}")
        print(f"Patients without CAC scores: {len(patients_without_scores)}")
        
        if patients_with_scores:
            print(f"\n=== Patients WITH CAC Scores ===")
            for i, patient in enumerate(patients_with_scores[:10]):  # Show first 10
                print(f"{i+1}. Patient ID: {patient['patient_id']}, Score: {patient['score_value']}")
            
            if len(patients_with_scores) > 10:
                print(f"... and {len(patients_with_scores) - 10} more patients")
        
        # Save results to a new file
        output_file = "/home/mirulab02/ekg-rama/patients_with_cac_scores.csv"
        if patients_with_scores:
            result_df = pd.DataFrame(patients_with_scores)
            result_df.to_csv(output_file, index=False)
            print(f"\nResults saved to: {output_file}")
        
        return patients_with_scores
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def analyze_output_csv_structure():
    """
    Analyze the structure of output.csv to understand its contents
    """
    csv_path = "/home/mirulab02/ekg-rama/output.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return
    
    try:
        df = pd.read_csv(csv_path)
        print("=== CSV Structure Analysis ===")
        print(f"Shape: {df.shape}")
        print("\nColumn names:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        print(f"\nFirst few rows:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"Error analyzing CSV structure: {e}")
        return None

if __name__ == "__main__":
    print("Analyzing output.csv for CAC score data...")
    print("=" * 60)
    
    # First, analyze the structure
    df = analyze_output_csv_structure()
    
    if df is not None:
        print("\n" + "=" * 60)
        
        # Then identify patients with scores
        patients_with_scores = identify_patients_with_cac_scores()
        
        print("\n" + "=" * 60)
        print("Analysis complete!")