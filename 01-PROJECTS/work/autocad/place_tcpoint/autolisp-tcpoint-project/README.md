# AutoLISP TCPOINT Project

## Overview
The AutoLISP TCPOINT project provides functionality for placing TCPOINT blocks at the ends of lines and polylines in AutoCAD. This project includes various utility functions, configuration options, and commands to facilitate the placement of these blocks, enhancing the drawing process.

## Features
- **Automatic and Manual Placement**: Users can choose between automatic detection of centers and manual selection of lines and polylines for block placement.
- **Configuration Options**: Easily modify parameters such as block name, layer suffix, and proximity radius to suit your needs.
- **Utility Functions**: Includes functions for geometric calculations, layer management, and block operations.

## Installation
1. Clone the repository to your local machine:
   ```
   git clone <repository-url>
   ```
2. Open AutoCAD and load the AutoLISP files from the `src/main` directory.
3. Ensure that the required block files are available in the `resources/blocks` directory.

## Usage
- Load the main command by typing `PLACE-TCPOINT` in the AutoCAD command line.
- Follow the prompts to select lines or polylines and place TCPOINT blocks accordingly.

## Documentation
- For detailed usage instructions, refer to the [User Manual](docs/user-manual.md).
- For API details, see the [API Reference](docs/api-reference.md).

## Examples
- Sample drawings demonstrating the use of TCPOINT blocks can be found in the `examples/sample-drawings` directory.
- Example scripts for using the TCPOINT placement commands are available in `examples/usage-examples.lsp`.

## Testing
- Unit tests for geometry functions are located in `tests/test-geometry.lsp`.
- Tests for placement commands can be found in `tests/test-placement.lsp`.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.