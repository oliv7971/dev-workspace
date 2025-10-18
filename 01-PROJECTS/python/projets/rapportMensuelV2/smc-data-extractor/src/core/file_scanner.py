import os
import re

def scan_directory(root_folder):
    smc_files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if 'SMC' in filename:
                smc_files.append(os.path.join(dirpath, filename))
    return smc_files

def filter_excel_files(file_list):
    return [file for file in file_list if file.endswith(('.xlsm', '.xlsx'))]

def find_relevant_files(root_folder):
    all_files = scan_directory(root_folder)
    return filter_excel_files(all_files)