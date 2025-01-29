from typing import Dict, Any

# DB ENGINES
# --------------------------------------------------------

MONGO = "mongodb"
POSTGRES = "postgres"
ORACLE = "oracle"
REDIS = "redis"
DB_ENGINES = [MONGO, POSTGRES, ORACLE, REDIS]

# APP ENGINES
# --------------------------------------------------------
ONESTREAM = "onestream"
APPLICATION_ENGINES = [ONESTREAM]

SYS_METADATA_COLLECTION = "sys_metadata"
SYS_USER_COLLECTION = "sys_users"
SYS_USER_GROUP_COLLECTION = "sys_user_groups"

SYS_COLLECTION_PREFIX = "sys_"
TEMP_COLLEXTION_PREFIX = "temp_"

CONSTRAINT_PREFIX = [SYS_COLLECTION_PREFIX, TEMP_COLLEXTION_PREFIX]

# MONGO DB
# --------------------------------------------------------

ENGINES_COLLECTION = "engines"
TEMP_USER_ID = "temp_user_id"

# Available operator for database querying
# --------------------------------------------------------
EQUAL = "eq"
NOT_EQUAL = "neq"
GREATER_THAN = "gt"
GREATER_THAN_EQUAL = "gte"
LESS_THAN = "lt"
LESS_THAN_EQUAL = "lte"
IN = "in"
NOT_IN = "nin"
LIKE = "like"
NOT_LIKE = "nlike"
SUM_GROUP = "sum_group"

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
    SUM_GROUP,
]


# Connections
# ---------------------------------------------------------
# Store the existing and open connections
existing_connections: Dict[str, Dict[str, Any]] = {}

MAX_LIMIT_QUERY = 100
