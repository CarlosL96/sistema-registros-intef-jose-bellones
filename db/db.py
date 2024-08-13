import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import os

# Función para cargar variables de entorno desde .env


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=env_path)


def getConnection():
    # Obtener variables de entorno
    host = os.getenv('DB_HOST')
    database = os.getenv('DB_DATABASE')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    pool_name = os.getenv('DB_POOL_NAME')
    pool_size = int(os.getenv('DB_POOL_SIZE'))

    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    return connection


# Función para crear el pool de conexiones
def createConnectionPool():
    load_env()

    # Obtener variables de entorno
    host = os.getenv('DB_HOST')
    database = os.getenv('DB_DATABASE')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    pool_name = os.getenv('DB_POOL_NAME')
    pool_size = int(os.getenv('DB_POOL_SIZE'))

    # Configurar el pool de conexiones
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name=pool_name,
        pool_size=pool_size,
        pool_reset_session=False,
        host=host,
        database=database,
        user=user,
        password=password,

    )

    return connection_pool
