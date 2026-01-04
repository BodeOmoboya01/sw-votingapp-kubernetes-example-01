"""
Vote Application - Flask-based voting frontend
Allows users to vote between two options (Cats vs Dogs)
Stores votes in Redis for the worker to process
"""

import os
import socket
import redis
from flask import Flask, render_template, request, make_response, g

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
OPTION_A = os.getenv('OPTION_A', 'Cats')
OPTION_B = os.getenv('OPTION_B', 'Dogs')

app = Flask(__name__)


def get_redis():
    """Get Redis connection, creating one if needed"""
    if not hasattr(g, 'redis'):
        g.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
    return g.redis


def get_voter_id(request, response):
    """Get or create a unique voter ID from cookies"""
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(hash(f"{request.remote_addr}-{socket.gethostname()}"))[2:18]
        response.set_cookie('voter_id', voter_id, max_age=86400 * 365)
    return voter_id


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main voting page"""
    vote = None
    hostname = socket.gethostname()
    
    # Prepare response
    response = make_response()
    voter_id = get_voter_id(request, response)
    
    if request.method == 'POST':
        vote = request.form.get('vote')
        if vote in ['a', 'b']:
            try:
                r = get_redis()
                # Push vote to Redis queue as JSON
                data = f'{{"voter_id": "{voter_id}", "vote": "{vote}"}}'
                r.rpush('votes', data)
                app.logger.info(f"Vote recorded: {voter_id} -> {vote}")
            except redis.RedisError as e:
                app.logger.error(f"Redis error: {e}")
    
    # Render template with response
    response = make_response(render_template(
        'index.html',
        option_a=OPTION_A,
        option_b=OPTION_B,
        hostname=hostname,
        vote=vote
    ))
    
    # Ensure voter_id cookie is set
    if not request.cookies.get('voter_id'):
        response.set_cookie('voter_id', voter_id, max_age=86400 * 365)
    
    return response


@app.route('/health')
def health():
    """Health check endpoint for Kubernetes"""
    try:
        r = get_redis()
        r.ping()
        return {'status': 'healthy', 'redis': 'connected'}, 200
    except redis.RedisError:
        return {'status': 'unhealthy', 'redis': 'disconnected'}, 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.getenv('DEBUG', 'false').lower() == 'true')
