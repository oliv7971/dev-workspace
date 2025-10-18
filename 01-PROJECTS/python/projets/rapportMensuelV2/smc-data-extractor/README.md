# SMC Data Extractor

## Overview

The SMC Data Extractor is a Python application designed to automate the extraction, processing, and reporting of measurement data from Excel files related to Sections de Convergence (SMC). The tool is capable of handling various file structures and formats, providing users with a streamlined way to analyze and visualize data.

## Features

- **File Exploration**: Recursively scans directories to identify relevant SMC Excel files.
- **Data Extraction**: Automatically extracts convergence and displacement data from Excel files, accommodating variations in file structure.
- **Calculations**: Computes periodic and cumulative changes in measurements.
- **CSV Exports**: Generates normalized CSV files for dates, convergences, and displacements.
- **PDF Reports**: Produces PDF documents containing tables and graphs for each Excel file processed.
- **User Interface**: Provides a graphical user interface for selecting input and output directories and specifying the month for analysis.

## Project Structure

```
smc-data-extractor
├── src
│   ├── core
│   ├── exporters
│   ├── models
│   ├── utils
│   └── smc_gui.py
│   └── smc_evolutions.py
│   └── produire_recaps.py
├── config
├── docs
├── tests
├── requirements.txt
└── setup.py
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd smc-data-extractor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `config/settings.yaml` and `config/regex_patterns.yaml` as needed.

## Usage

To run the application, execute the following command:
```
python src/smc_gui.py
```

Follow the prompts in the graphical user interface to select the root folder containing the Excel files, specify the month for analysis, and choose the output folder for the generated reports.

## Testing

Unit tests are provided in the `tests` directory. To run the tests, use:
```
pytest tests
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.