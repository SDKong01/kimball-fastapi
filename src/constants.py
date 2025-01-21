from typing import Dict, Any

# DB ENGINES
# --------------------------------------------------------

MONGO = "mongodb"
POSTGRES = "postgres"
ORACLE = "oracle"
REDIS = "redis"
DB_ENGINES = [MONGO, POSTGRES, ORACLE, REDIS]

# MONGO DB
# --------------------------------------------------------

ENGINES_COLLECTION = "engines"
TEMP_USER_ID = "temp_user_id"

# Available operator for database querying
# --------------------------------------------------------
EQUAL = "eq"
NOT_EQUAL = "ne"
GREATER_THAN = "gt"
GREATER_THAN_EQUAL = "gte"
LESS_THAN = "lt"
LESS_THAN_EQUAL = "lte"
IN = "in"
NOT_IN = "nin"
LIKE = "like"
NOT_LIKE = "nlike"

DB_OPERATORS = [
    EQUAL,
    NOT_EQUAL,
    GREATER_THAN,
    GREATER_THAN_EQUAL,
    LESS_THAN,
    LESS_THAN_EQUAL,
    IN,
    NOT_IN,
    LIKE,
    NOT_LIKE,
]


# Connections
# ---------------------------------------------------------
# Store the existing and open connections
existing_connections: Dict[str, Dict[str, Any]] = {}
