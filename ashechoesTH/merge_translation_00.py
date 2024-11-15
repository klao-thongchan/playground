import pandas as pd

def merge_excel_files(source_path, merge_path, output_path):
    """
    Merge two Excel files based on column A as key, with merge_file taking precedence
    Handles duplicate keys by keeping the latest occurrence
    
    Parameters:
    source_path (str): Path to the source Excel file
    merge_path (str): Path to the file to merge
    output_path (str): Path where the output file will be saved
    """
    try:
        # Read both Excel files
        source_df = pd.read_excel(source_path)
        merge_df = pd.read_excel(merge_path)
        
        # Get the name of the first column (key column)
        key_column = source_df.columns[0]
        
        # Convert key column to string and strip any whitespace
        source_df[key_column] = source_df[key_column].astype(str).str.strip()
        merge_df[key_column] = merge_df[key_column].astype(str).str.strip()
        
        # Create dictionaries to store the latest version of each row
        source_dict = {row[key_column]: row.to_dict() for _, row in source_df.iterrows()}
        merge_dict = {row[key_column]: row.to_dict() for _, row in merge_df.iterrows()}
        
        # Update source_dict with merge_dict
        for key, merge_row in merge_dict.items():
            source_dict[key] = merge_row
        
        # Create final dataframe from the merged dictionary
        final_df = pd.DataFrame.from_dict(source_dict, orient='index')
        
        # Reset index to make the key column a regular column again
        final_df.reset_index(inplace=True)
        
        # Rename 'index' column back to original key column name if needed
        if 'index' in final_df.columns:
            final_df.rename(columns={'index': key_column}, inplace=True)
        
        # Reorder columns to match original source file
        final_df = final_df[source_df.columns]
        
        # Save the merged result
        final_df.to_excel(output_path, index=False)
        
        # Print merge statistics
        total_rows = len(final_df)
        original_rows = len(source_df)
        unique_keys_source = len(set(source_df[key_column]))
        unique_keys_merge = len(set(merge_df[key_column]))
        unique_keys_final = len(set(final_df[key_column]))
        
        print(f"\nMerge Statistics:")
        print(f"Original rows in source file: {original_rows}")
        print(f"Unique keys in source file: {unique_keys_source}")
        print(f"Unique keys in merge file: {unique_keys_merge}")
        print(f"Total rows in final file: {total_rows}")
        print(f"Unique keys in final file: {unique_keys_final}")
        print(f"\nSuccessfully merged files and saved to {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise  # Re-raise the exception to see the full error trace if needed

# Updated file names
if __name__ == "__main__":
    source_file = "th_full_1113_HB.xlsx"
    merge_file = "th_full_1115_tomerge.xlsx"
    output_file = "th_full_1115_HB.xlsx"
    
    merge_excel_files(source_file, merge_file, output_file)