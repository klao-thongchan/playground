import pandas as pd

def merge_excel_files(source_path, merge_path, output_path):
    """
    Merge two Excel files based on column A as key, with merge_file taking precedence
    
    Parameters:
    source_path (str): Path to the source Excel file
    merge_path (str): Path to the file to merge
    output_path (str): Path where the output file will be saved
    """
    try:
        # Read both Excel files
        source_df = pd.read_excel(source_path)
        merge_df = pd.read_excel(merge_path)
        
        # Ensure column A (index 0) is used as key
        key_column = source_df.columns[0]
        
        # Convert key column to string in both dataframes to ensure consistent matching
        source_df[key_column] = source_df[key_column].astype(str)
        merge_df[key_column] = merge_df[key_column].astype(str)
        
        # Set the key column as index for both dataframes
        source_df.set_index(key_column, inplace=True)
        merge_df.set_index(key_column, inplace=True)
        
        # Update existing rows in source_df with merge_df data
        source_df.update(merge_df)
        
        # Append new rows from merge_df that don't exist in source_df
        new_rows = merge_df.loc[~merge_df.index.isin(source_df.index)]
        final_df = pd.concat([source_df, new_rows])
        
        # Reset index to make the key column visible again
        final_df.reset_index(inplace=True)
        
        # Save the merged result
        final_df.to_excel(output_path, index=False)
        
        print(f"Successfully merged files and saved to {output_path}")
        
        # Print some merge statistics
        total_rows = len(final_df)
        updated_rows = len(source_df.index.intersection(merge_df.index))
        new_rows = len(new_rows)
        
        print(f"\nMerge Statistics:")
        print(f"Total rows in final file: {total_rows}")
        print(f"Updated rows: {updated_rows}")
        print(f"New rows added: {new_rows}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    source_file = "source_file.xlsx"
    merge_file = "merge_file.xlsx"
    output_file = "output_file.xlsx"
    
    merge_excel_files(source_file, merge_file, output_file)