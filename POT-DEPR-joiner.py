import os
import numpy as np
import pandas as pd

# sth similar to IIFE
main = lambda f: f()
@main
def main():
    global data
    print('\n \tStarting the JOINER script for potentiation-depression files...')
    print('\nPut all of the PAIRS of pot-depr CAs in ONE folder to be scanned')

    # The directory where files are located. Can be full path or just the name if the directory is in the PyCharm project folder
    directory = "dataCA"

    # List all files in the directory
    files = os.listdir(directory)
    print(files)

    # Group files by their prefixes (e.g., switch2v_02_, switch2v_03_, switch4v_02_, switch4v_03_,)
    file_groups = {}

    for file in files:
        prefix = file.split('x_')[0]  # Extract prefix (e.g., file01a -> file01)
        # print('PREFIXes: ')
        # print(prefix)

        if prefix not in file_groups:
            file_groups[prefix] = []
            print('PREFIX: ')
            print('\r', prefix)
        file_groups[prefix].append(file)


    # Iterate over file groups (pairs of files with the same prefix)
    combined_dfs = pd.DataFrame()
    # Initialize an empty DataFrame to store concatenated file01 and file02 vertically
    result_df = pd.DataFrame()

    # Iterate over file groups (pairs of files with the same prefix)
    for prefix, file_list in file_groups.items():


        # Find the index of "switch" in the prefix
        print('\n Working with file:')
        print(file_list[1])
        start_index = file_list[1].find("switch")
        print("start index: ", start_index)
        stop_index = file_list[1].find("_03_CA_")
        print("stop index: ", stop_index)

        if len(file_list) == 2:  # Ensure there are two files with the same prefix

            if start_index != -1 and stop_index != -1:  # Check if both substrings are found
                # Slice the prefix string to show what is between start and stop indices
                substring_between_indices = file_list[1][start_index + len("switch"):stop_index]
                print("Substring between 'switch' and '_03_CA_':", substring_between_indices)
            else:
                print("Either 'switch' or '_03_CA_' not found in the filename")

        # Compose file paths
        file01_path = os.path.join(directory, file_list[0])
        file02_path = os.path.join(directory, file_list[1])

        # Read files with headers
        file01 = pd.read_csv(file01_path, delimiter='\t')
        file02 = pd.read_csv(file02_path, delimiter='\t')

        # Find the maximum cycle value in file01
        max_cycle_file01 = file01['cycle'].max()
        # Start cycle count for the file _03_ where _02_ ended
        file02['cycle'] += max_cycle_file01 + 1

        file01['pot-depr'] = 1
        file02['pot-depr'] = 2

        # Add 1st line below the headers - for ORIGIN file import - units
        units_line = {'cycle': np.nan, 'pot-depr': np.nan, 'I_read/mA': np.nan}
        units = pd.DataFrame([units_line])

        # Add 2nd line below the headers - for ORIGIN file import - comments
        #Also - replace the description to a number
        # Extract substring between 'p' and 'v'
        substring=substring_between_indices
        substring_extracted = substring.split('v', 1)[0]

        parts = substring_extracted.split('p')
        integer_part = parts[0]
        fractional_part = parts[1]
        # Convert the parts to float and combine them
        value = float(integer_part + '.' + fractional_part)
        print("value:",value)

        #comments_line = {'cycle': np.nan, 'pot-depr': np.nan, 'I_read/mA': substring_between_indices} #0p80v
        comments_line = {'cycle': np.nan, 'pot-depr': np.nan, 'I_read/mA': value} #0.8
        comments = pd.DataFrame([comments_line])

        # Check if the 'cycle' column exists
        # if 'cycle' in combined_dfs.any():
        if 'cycle' in result_df.any():
            results_column = ['I_read/mA']
        else:
            results_column = ['cycle', 'pot-depr', 'I_read/mA']

        # Concatenate the DataFrames along columns
        combined_df = pd.concat(
            [units[results_column], comments[results_column], file01[results_column], file02[results_column]],
            ignore_index=True)

        # Append the concatenated DataFrame as a new column to combined_dfs
        result_df = pd.concat([result_df, combined_df], axis=1)
        #prints below can be commented
        print("RESULT (iteratively):\n", result_df)
        # Now combined_dfs contains the concatenated DataFrame as a new column
        print(result_df)
        # result_df = pd.concat([result_df, combined_df], axis=1)

    # Output the combined DataFrame
    # prints below can be commented
    print("FINAL DataFrame:")
    print(result_df)
    # Confirm the file has been saved
    output_filename = "00_pot_depr_combined_file"
    print("File saved as", output_filename +".txt")
    result_df.to_csv(output_filename +".txt", sep='\t', index=False)

del(main)