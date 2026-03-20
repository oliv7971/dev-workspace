# Configuration settings for the road axis calculator application

# Constants for application settings
AXIS_DEFAULT_LENGTH = 1000  # Default length of the road axis in meters
POINT_DEFAULT_ELEVATION = 0  # Default elevation for points in meters
TUNNEL_DEFAULT_HEIGHT = 4.5   # Default height of the tunnel in meters
TUNNEL_DEFAULT_WIDTH = 5.0    # Default width of the tunnel in meters

# Application version
APP_VERSION = "1.0.0"

# Logging settings
LOGGING_LEVEL = "DEBUG"  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Database settings (if applicable)
DATABASE_URL = "sqlite:///road_axis_calculator.db"  # Default database URL for SQLite

# Other configuration settings can be added as needed