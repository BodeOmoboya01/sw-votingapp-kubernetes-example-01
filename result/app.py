"""
Result Application - Flask-based results frontend
Displays real-time voting results from PostgreSQL
Uses Server-Sent Events (SSE) for live updates
"""

import os
import json
import socket
import time
import threading
import psycopg2
from flask import Flask, render_template, Response, jsonify

# Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
OPTION_A = os.getenv('OPTION_A', 'Cats')
OPTION_B = os.getenv('OPTION_B', 'Dogs')

app = Flask(__name__)

# Cache for results
results_cache = {'a': 0, 'b': 0, 'total': 0}
cache_lock = threading.Lock()


def get_postgres_connection():
    """Create PostgreSQL connection with retry logic"""
    max_retries = 5
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
            return conn
        except psycopg2.Error as e:
            app.logger.warning(f"PostgreSQL connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    return None


def fetch_results():
    """Fetch voting results from PostgreSQL"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return None
            
        with conn.cursor() as cur:
            # Get vote counts
            cur.execute("""
                SELECT vote, COUNT(*) as count 
                FROM votes 
                GROUP BY vote
            """)
            results = cur.fetchall()
            
        conn.close()
        
        # Process results
        vote_counts = {'a': 0, 'b': 0}
        for row in results:
            vote, count = row
            if vote in vote_counts:
                vote_counts[vote] = count
        
        total = vote_counts['a'] + vote_counts['b']
        
        return {
            'a': vote_counts['a'],
            'b': vote_counts['b'],
            'total': total
        }
        
    except psycopg2.Error as e:
        app.logger.error(f"Database error: {e}")
        return None


def update_cache():
    """Background thread to update results cache"""
    global results_cache
    while True:
        try:
            results = fetch_results()
            if results:
                with cache_lock:
                    results_cache = results
        except Exception as e:
            app.logger.error(f"Cache update error: {e}")
        time.sleep(1)  # Update every second


# Start background cache updater
cache_thread = threading.Thread(target=update_cache, daemon=True)
cache_thread.start()


@app.route('/')
def index():
    """Main results page"""
    hostname = socket.gethostname()
    return render_template(
        'index.html',
        option_a=OPTION_A,
        option_b=OPTION_B,
        hostname=hostname
    )


@app.route('/api/results')
def api_results():
    """API endpoint for current results"""
    with cache_lock:
        return jsonify(results_cache)


@app.route('/stream')
def stream():
    """Server-Sent Events endpoint for real-time updates"""
    def generate():
        last_data = None
        while True:
            with cache_lock:
                current_data = dict(results_cache)
            
            # Only send if data changed
            if current_data != last_data:
                yield f"data: {json.dumps(current_data)}\n\n"
                last_data = current_data
            
            time.sleep(0.5)
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/health')
def health():
    """Health check endpoint for Kubernetes"""
    conn = get_postgres_connection()
    if conn:
        conn.close()
        return {'status': 'healthy', 'postgres': 'connected'}, 200
    return {'status': 'unhealthy', 'postgres': 'disconnected'}, 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.getenv('DEBUG', 'false').lower() == 'true', threaded=True)
