import csv
import os

class CSVExporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def export_dates(self, dates_data):
        file_path = os.path.join(self.output_dir, 'Dates.csv')
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['source_file', 'sheet', 'galerie', 'section', 'month', 'dates_in_month'])
            for row in dates_data:
                writer.writerow(row)

    def export_convergences(self, convergences_data):
        file_path = os.path.join(self.output_dir, 'Convergences.csv')
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['source_file', 'sheet', 'galerie', 'section', 'month', 'metric', 
                             'periodic_mm', 'cumulative_mm', 'date_last_in_month', 
                             'date_last_before_month', 'date_last_global', 
                             'cumul_out_of_month', 'duplicate_day'])
            for row in convergences_data:
                writer.writerow(row)

    def export_deplacements(self, deplacements_data):
        file_path = os.path.join(self.output_dir, 'Deplacements.csv')
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['source_file', 'sheet', 'galerie', 'section', 'month', 
                             'metric_axis', 'metric_pos', 'periodic_mm', 
                             'cumulative_mm', 'date_last_in_month', 
                             'date_last_before_month', 'date_last_global', 
                             'cumul_out_of_month', 'duplicate_day'])
            for row in deplacements_data:
                writer.writerow(row)