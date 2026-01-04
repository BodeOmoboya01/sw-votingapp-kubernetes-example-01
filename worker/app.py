"""
Worker Application - Background vote processor
Reads votes from Redis queue and stores them in PostgreSQL
"""

import os
import json
import time
import logging
import signal
import sys
import redis
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('worker')

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')

# Graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def get_redis_connection():
    """Create Redis connection with retry logic"""
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            r.ping()
            logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            return r
        except redis.RedisError as e:
            logger.warning(f"Redis connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    raise Exception("Could not connect to Redis after multiple attempts")


def get_postgres_connection():
    """Create PostgreSQL connection with retry logic"""
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                database=POSTGRES_DB,
                connect_timeout=5
            )
            logger.info(f"Connected to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}")
            return conn
        except psycopg2.Error as e:
            logger.warning(f"PostgreSQL connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    raise Exception("Could not connect to PostgreSQL after multiple attempts")


def init_database(conn):
    """Initialize the database schema"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id VARCHAR(255) PRIMARY KEY,
                vote VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_votes_vote ON votes(vote)
        """)
        
        conn.commit()
        logger.info("Database schema initialized")


def process_vote(conn, voter_id, vote):
    """Process a single vote - upsert into PostgreSQL"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO votes (id, vote, updated_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (id) 
            DO UPDATE SET vote = EXCLUDED.vote, updated_at = CURRENT_TIMESTAMP
        """, (voter_id, vote))
        conn.commit()
        logger.info(f"Processed vote: {voter_id} -> {vote}")


def main():
    """Main worker loop"""
    logger.info("Starting vote worker...")
    
    # Connect to Redis
    redis_conn = get_redis_connection()
    
    # Connect to PostgreSQL
    pg_conn = get_postgres_connection()
    
    # Initialize database
    init_database(pg_conn)
    
    logger.info("Worker ready, waiting for votes...")
    
    while not shutdown_requested:
        try:
            # Blocking pop from Redis queue with 1 second timeout
            result = redis_conn.blpop('votes', timeout=1)
            
            if result:
                _, vote_data = result
                try:
                    # Parse vote data
                    data = json.loads(vote_data.decode('utf-8'))
                    voter_id = data.get('voter_id')
                    vote = data.get('vote')
                    
                    if voter_id and vote:
                        process_vote(pg_conn, voter_id, vote)
                    else:
                        logger.warning(f"Invalid vote data: {data}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse vote data: {e}")
                    
        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            # Attempt to reconnect
            time.sleep(2)
            try:
                redis_conn = get_redis_connection()
            except Exception:
                pass
                
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL error: {e}")
            # Attempt to reconnect
            time.sleep(2)
            try:
                pg_conn = get_postgres_connection()
            except Exception:
                pass
    
    # Cleanup
    logger.info("Shutting down worker...")
    try:
        redis_conn.close()
        pg_conn.close()
    except Exception:
        pass
    
    logger.info("Worker shutdown complete")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)
