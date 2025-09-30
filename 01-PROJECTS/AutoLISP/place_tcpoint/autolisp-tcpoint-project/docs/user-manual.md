# User Manual for TCPOINT Placement Project

## Introduction

The TCPOINT Placement Project provides functionality for placing TCPOINT blocks at the ends of lines and polylines within AutoCAD. This manual will guide you through the installation, configuration, and usage of the project.

## Installation

1. **Download the Project**: Clone or download the repository from the source.
2. **Load the LISP Files**: Open AutoCAD and load the LISP files located in the `src/main` directory. You can do this by using the `APPLOAD` command in AutoCAD.

## Configuration

Before using the TCPOINT placement functionality, you may want to configure the parameters to suit your needs. The configuration settings can be modified in the `config-tcpoint.lsp` file. The following parameters can be adjusted:

- **Block Name**: The name of the block to be inserted (default: "TCPOINT").
- **Layer Suffix**: The suffix to be added to the layer of the line (default: "_tete").
- **Proximity Radius**: The default proximity radius for detecting centers (default: 10.0 meters).

## Usage

### Commands

The following commands are available for placing TCPOINT blocks:

- **PLACE-TCPOINT**: This command initiates the placement of TCPOINT blocks. It offers four modes of operation:
  1. **Automatic**: Automatically detects centers and places TCPOINT blocks on all lines and polylines.
  2. **Semi-Automatic**: Automatically detects centers but allows for manual selection of entities.
  3. **Manual**: Requires the user to specify a center point and select lines or polylines manually.
  4. **Auto-Create**: Creates intersection centers automatically and places TCPOINT blocks accordingly.

### Example Usage

To place TCPOINT blocks automatically, type the following command in AutoCAD:

```
PLACE-TCPOINT
```

Follow the prompts to select the desired mode and proceed with the placement.

## Testing

The project includes test scripts located in the `tests` directory. These scripts can be used to verify the functionality of the geometry calculations and placement commands. To run the tests, load the respective test files in AutoCAD and execute the commands defined within them.

## Conclusion

This user manual provides a comprehensive overview of the TCPOINT Placement Project. For further assistance, please refer to the API reference or contact the project maintainers.