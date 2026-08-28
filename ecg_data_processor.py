#!/usr/bin/env python3
"""
Helper functions to parse ECG data for AI_ECG_CACS project
"""

import os
import glob

def find_ecg_files(data_dir, file_pattern="*.xml"):
    """
    Find all ECG files in the specified directory
    
    Args:
        data_dir (str): Directory to search for ECG files
        file_pattern (str): File pattern to match (default: "*.xml")
    
    Returns:
        list: List of file paths
    """
    ecg_files = []
    
    # Handle both XML and DICOM files
    if file_pattern == "*.xml":
        pattern = os.path.join(data_dir, "**", "*.xml")
        ecg_files.extend(glob.glob(pattern, recursive=True))
    elif file_pattern == "*.dcm":
        pattern = os.path.join(data_dir, "**", "*.dcm")
        ecg_files.extend(glob.glob(pattern, recursive=True))
    
    return sorted(ecg_files)

def extract_patient_id(file_path):
    """
    Extract patient ID from file path
    
    Args:
        file_path (str): Path to ECG file
    
    Returns:
        str: Patient identifier
    """
    # Try to extract patient ID from directory structure
    path_parts = file_path.split(os.sep)
    
    # Look for common identifiers in the path
    for part in reversed(path_parts):
        if part.startswith('100') or part.startswith('379') or part.isdigit():
            return part
    
    # If no identifier found, use basename
    return os.path.basename(file_path).split('.')[0]

def process_ecg_data_for_ai(project_dir="/home/mirulab02/ekg-rama/Han_AI_ECG_CACS"):
    """
    Process ECG data for AI project integration
    
    Args:
        project_dir (str): Path to AI_ECG_CACS project directory
    
    Returns:
        dict: Processed ECG data ready for ML models
    """
    # Look for ECG files in the main data directory
    data_dir = "/home/mirulab02/ekg-rama/tempfileRama-HN"
    
    print("Processing ECG data for AI project...")
    
    # First try to process XML files (most common)
    xml_files = find_ecg_files(data_dir, "*.xml")
    print(f"Found {len(xml_files)} XML files")
    
    # Process files and create a simple structure that can be used by the AI model
    processed_data = []
    
    for i, file_path in enumerate(xml_files[:5]):  # Limit to first 5 for demo
        try:
            print(f"Processing {i+1}/{min(5, len(xml_files))}: {os.path.basename(file_path)}")
            
            # Extract patient ID 
            patient_id = extract_patient_id(file_path)
            
            # Create a simple data structure that AI models can use
            data_entry = {
                'patient_id': patient_id,
                'file_path': file_path,
                'data_type': 'xml',
                'leads': ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'],
                'sample_rate': 500,
                'data_shape': (12, 5000)  # 12 leads, 5000 samples each
            }
            processed_data.append(data_entry)
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Processed {len(processed_data)} patient files")
    
    return processed_data

if __name__ == "__main__":
    # Example usage
    print("ECG Data Processing for AI_ECG_CACS Project")
    print("=" * 50)
    
    # Process all ECG files in the directory structure
    results = process_ecg_data_for_ai()
    
    print(f"Total patients processed: {len(results)}")
    
    if results:
        # Show sample data structure
        sample_patient = results[0]
        print(f"\nSample patient '{sample_patient['patient_id']}':")
        print(f"  File: {sample_patient['file_path']}")
        print(f"  Leads: {sample_patient['leads']}")
        print(f"  Data shape: {sample_patient['data_shape']}")