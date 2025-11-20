"""
Multiplayer Server for Castle Strategy Game
Handles matchmaking, game rooms, and state synchronization
"""

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_cors import CORS
import uuid
import time
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'castle-strategy-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Game state
waiting_players = []  # Players waiting for match
active_games = {}  # game_id -> game_data
player_to_game = {}  # player_id -> game_id
player_sockets = {}  # player_id -> socket_id


class GameRoom:
    """Represents a multiplayer game room"""

    def __init__(self, game_id, player1_id, player2_id):
        self.game_id = game_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.player1_ready = False
        self.player2_ready = False
        self.started = False
        self.created_at = time.time()

        # Game state
        self.game_state = {
            'player1': {
                'castle_hp': 10000,
                'gold': 1000,
                'mines': 0,
                'units': [],
                'spell_cooldowns': {}
            },
            'player2': {
                'castle_hp': 10000,
                'gold': 1000,
                'mines': 0,
                'units': [],
                'spell_cooldowns': {}
            }
        }

    def get_player_role(self, player_id):
        """Get player's role (player1 or player2)"""
        if player_id == self.player1_id:
            return 'player1'
        elif player_id == self.player2_id:
            return 'player2'
        return None

    def get_opponent_id(self, player_id):
        """Get opponent's player ID"""
        if player_id == self.player1_id:
            return self.player2_id
        return self.player1_id

    def both_ready(self):
        """Check if both players are ready"""
        return self.player1_ready and self.player2_ready


@app.route('/')
def index():
    """Health check endpoint"""
    return {
        'status': 'online',
        'active_games': len(active_games),
        'waiting_players': len(waiting_players)
    }


@socketio.on('connect')
def handle_connect():
    """Handle player connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'player_id': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle player disconnection"""
    player_id = request.sid
    print(f'Client disconnected: {player_id}')

    # Remove from waiting queue
    if player_id in waiting_players:
        waiting_players.remove(player_id)

    # Handle game disconnect
    if player_id in player_to_game:
        game_id = player_to_game[player_id]
        if game_id in active_games:
            game = active_games[game_id]
            opponent_id = game.get_opponent_id(player_id)

            # Notify opponent
            if opponent_id in player_sockets:
                socketio.emit('opponent_disconnected',
                            {'reason': 'Player left the game'},
                            room=player_sockets[opponent_id])

            # Clean up game
            del active_games[game_id]
            del player_to_game[player_id]
            if opponent_id in player_to_game:
                del player_to_game[opponent_id]

    # Clean up socket mapping
    if player_id in player_sockets:
        del player_sockets[player_id]


@socketio.on('find_match')
def handle_find_match():
    """Handle matchmaking request"""
    player_id = request.sid
    player_sockets[player_id] = request.sid

    print(f'Player {player_id} looking for match')

    # Check if there's a waiting player
    if waiting_players:
        # Match with waiting player
        opponent_id = waiting_players.pop(0)

        # Create game room
        game_id = str(uuid.uuid4())
        game = GameRoom(game_id, player_id, opponent_id)
        active_games[game_id] = game
        player_to_game[player_id] = game_id
        player_to_game[opponent_id] = game_id

        # Join socket rooms
        join_room(game_id, sid=player_id)
        join_room(game_id, sid=opponent_id)

        # Notify both players
        emit('match_found', {
            'game_id': game_id,
            'role': 'player1',
            'opponent': opponent_id
        }, room=player_id)

        socketio.emit('match_found', {
            'game_id': game_id,
            'role': 'player2',
            'opponent': player_id
        }, room=opponent_id)

        print(f'Match created: {game_id} - {player_id} vs {opponent_id}')
    else:
        # Add to waiting queue
        waiting_players.append(player_id)
        emit('searching', {'message': 'Searching for opponent...'})
        print(f'Player {player_id} added to queue')


@socketio.on('cancel_search')
def handle_cancel_search():
    """Cancel matchmaking search"""
    player_id = request.sid
    if player_id in waiting_players:
        waiting_players.remove(player_id)
        emit('search_cancelled', {'message': 'Search cancelled'})


@socketio.on('ready')
def handle_ready(data):
    """Mark player as ready"""
    player_id = request.sid

    if player_id not in player_to_game:
        emit('error', {'message': 'Not in a game'})
        return

    game_id = player_to_game[player_id]
    game = active_games[game_id]
    role = game.get_player_role(player_id)

    if role == 'player1':
        game.player1_ready = True
    else:
        game.player2_ready = True

    # Check if both ready
    if game.both_ready() and not game.started:
        game.started = True
        socketio.emit('game_start', {
            'message': 'Both players ready! Game starting...'
        }, room=game_id)
        print(f'Game {game_id} started')
    else:
        emit('waiting_for_opponent', {'message': 'Waiting for opponent...'})


@socketio.on('unit_spawn')
def handle_unit_spawn(data):
    """Handle unit spawn event"""
    player_id = request.sid

    if player_id not in player_to_game:
        return

    game_id = player_to_game[player_id]
    game = active_games[game_id]
    role = game.get_player_role(player_id)
    opponent_id = game.get_opponent_id(player_id)

    # Broadcast to opponent
    if opponent_id in player_sockets:
        socketio.emit('opponent_unit_spawn', {
            'unit_type': data.get('unit_type'),
            'timestamp': time.time()
        }, room=player_sockets[opponent_id])


@socketio.on('spell_cast')
def handle_spell_cast(data):
    """Handle spell cast event"""
    player_id = request.sid

    if player_id not in player_to_game:
        return

    game_id = player_to_game[player_id]
    game = active_games[game_id]
    opponent_id = game.get_opponent_id(player_id)

    # Broadcast to opponent
    if opponent_id in player_sockets:
        socketio.emit('opponent_spell_cast', {
            'spell_name': data.get('spell_name'),
            'timestamp': time.time()
        }, room=player_sockets[opponent_id])


@socketio.on('mine_built')
def handle_mine_built(data):
    """Handle mine construction"""
    player_id = request.sid

    if player_id not in player_to_game:
        return

    game_id = player_to_game[player_id]
    game = active_games[game_id]
    role = game.get_player_role(player_id)

    # Update game state
    game.game_state[role]['mines'] += 1

    opponent_id = game.get_opponent_id(player_id)
    if opponent_id in player_sockets:
        socketio.emit('opponent_mine_built', {
            'mines': game.game_state[role]['mines']
        }, room=player_sockets[opponent_id])


@socketio.on('castle_damage')
def handle_castle_damage(data):
    """Handle castle damage event"""
    player_id = request.sid

    if player_id not in player_to_game:
        return

    game_id = player_to_game[player_id]
    game = active_games[game_id]
    opponent_id = game.get_opponent_id(player_id)

    # Notify opponent their castle took damage
    if opponent_id in player_sockets:
        socketio.emit('castle_damaged', {
            'damage': data.get('damage'),
            'new_hp': data.get('new_hp')
        }, room=player_sockets[opponent_id])


@socketio.on('game_over')
def handle_game_over(data):
    """Handle game over"""
    player_id = request.sid

    if player_id not in player_to_game:
        return

    game_id = player_to_game[player_id]
    game = active_games[game_id]
    opponent_id = game.get_opponent_id(player_id)

    # Notify both players
    winner = data.get('winner')
    socketio.emit('match_ended', {
        'winner': winner,
        'reason': data.get('reason', 'Castle destroyed')
    }, room=game_id)

    # Clean up
    del active_games[game_id]
    del player_to_game[player_id]
    if opponent_id in player_to_game:
        del player_to_game[opponent_id]


@socketio.on('ping')
def handle_ping():
    """Handle ping for latency measurement"""
    emit('pong', {'timestamp': time.time()})


if __name__ == '__main__':
    print('🏰 Castle Strategy Multiplayer Server Starting...')
    print('Server running on http://0.0.0.0:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
