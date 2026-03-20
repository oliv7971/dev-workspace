# Usage Instructions for Calage Coupes 3D

## Overview
The Calage Coupes 3D program is designed to automate the alignment of 3D cuts based on reference points. This document provides instructions on how to use the program effectively.

## Installation
1. Ensure you have AutoCAD installed on your system.
2. Place the `calage-coupes-3d` folder in a directory accessible by AutoCAD.
3. Load the main LISP file in AutoCAD using the command:
   ```
   (load "path/to/calage-coupes-3d/src/main.lsp")
   ```

## Commands
The program provides several commands for users:

### 1. CALAGE3D
- **Purpose**: Aligns selected 3D objects based on reference points from the `_CALAGE_PT` and `_CALAGE_3D_CI` layers.
- **Usage**: 
  - Type `CALAGE3D` in the command line and press Enter.
  - Follow the prompts to select the reference points and objects to align.

### 2. CALAGE3D-INFO
- **Purpose**: Displays information about the collected reference points and their correspondences.
- **Usage**: 
  - Type `CALAGE3D-INFO` in the command line and press Enter.
  - Review the output in the command line for details on reference points.

### 3. CALAGE3D-AUTO
- **Purpose**: Automates the alignment process for all cuts, processing them one by one.
- **Usage**: 
  - Type `CALAGE3D-AUTO` in the command line and press Enter.
  - The program will process each cut automatically, aligning objects based on the reference points.

## Example Workflow
1. Prepare your drawing with reference points on the `_CALAGE_PT` layer and 3D objects on the `_CALAGE_3D_CI` layer.
2. Load the main LISP file.
3. Run the `CALAGE3D` command to align specific objects.
4. Use `CALAGE3D-INFO` to check the reference points used.
5. For multiple cuts, run `CALAGE3D-AUTO` to automate the process.

## Notes
- Ensure that there are at least three reference points available for alignment.
- The program excludes points from the `_CALAGE_PT` layer when selecting objects for alignment.

For further assistance, refer to the README.md file or contact the project maintainers.