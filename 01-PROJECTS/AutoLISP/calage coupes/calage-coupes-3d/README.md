# Calage Coupes 3D

## Overview
The Calage Coupes 3D project is designed to automate the alignment of 3D cuts based on reference points. It provides a set of commands that allow users to perform 3D alignment efficiently by utilizing blocks and layers within a drawing environment.

## Purpose
This project aims to streamline the process of aligning 3D objects in CAD software by leveraging reference points defined in specific layers. It is particularly useful for architects, engineers, and designers who work with complex 3D models.

## Installation
To use the Calage Coupes 3D project, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd calage-coupes-3d
   ```

2. **Load the Program**
   Open your CAD software and load the main LISP file:
   ```lisp
   (load "src/main.lsp")
   ```

## Usage
The project includes several commands that can be executed within the CAD environment:

- **CALAGE3D**: Aligns 3D objects based on reference points collected from specific layers.
- **CALAGE3D-INFO**: Displays information about the collected reference points and their correspondences.
- **CALAGE3D-AUTO**: Automates the alignment process for all cuts, processing them one by one.

### Example
To perform a 3D alignment, use the following command:
```lisp
(CALAGE3D)
```

For automated processing of all cuts:
```lisp
(CALAGE3D-AUTO)
```

## Documentation
For detailed usage instructions and examples, refer to the [usage documentation](docs/usage.md).

## Testing
The project includes a sample drawing file located in the `tests` directory. This file can be used to test the functionality of the program.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.