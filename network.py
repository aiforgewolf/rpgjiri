"""
Network Manager for Multiplayer
Handles client-server communication
"""

try:
    import socketio
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("Warning: python-socketio not available. Multiplayer disabled.")


class NetworkManager:
    """Manages network communication for multiplayer"""

    def __init__(self):
        self.connected = False
        self.sio = None
        self.player_id = None
        self.game_id = None
        self.role = None  # 'player1' or 'player2'
        self.in_game = False
        self.opponent_actions = []

        if SOCKETIO_AVAILABLE:
            self.sio = socketio.Client()
            self.setup_handlers()

    def setup_handlers(self):
        """Setup event handlers"""
        if not self.sio:
            return

        @self.sio.on('connected')
        def on_connected(data):
            self.player_id = data['player_id']
            self.connected = True
            print(f'Connected to server as {self.player_id}')

        @self.sio.on('searching')
        def on_searching(data):
            print(data['message'])

        @self.sio.on('match_found')
        def on_match_found(data):
            self.game_id = data['game_id']
            self.role = data['role']
            self.in_game = True
            print(f'Match found! You are {self.role}')
            print(f'Game ID: {self.game_id}')

        @self.sio.on('game_start')
        def on_game_start(data):
            print(data['message'])

        @self.sio.on('opponent_unit_spawn')
        def on_opponent_unit_spawn(data):
            self.opponent_actions.append({
                'type': 'unit_spawn',
                'unit_type': data['unit_type'],
                'timestamp': data['timestamp']
            })

        @self.sio.on('opponent_spell_cast')
        def on_opponent_spell_cast(data):
            self.opponent_actions.append({
                'type': 'spell_cast',
                'spell_name': data['spell_name'],
                'timestamp': data['timestamp']
            })

        @self.sio.on('opponent_mine_built')
        def on_opponent_mine_built(data):
            self.opponent_actions.append({
                'type': 'mine_built',
                'mines': data['mines']
            })

        @self.sio.on('castle_damaged')
        def on_castle_damaged(data):
            self.opponent_actions.append({
                'type': 'castle_damage',
                'damage': data['damage'],
                'new_hp': data['new_hp']
            })

        @self.sio.on('opponent_disconnected')
        def on_opponent_disconnected(data):
            print(f'Opponent disconnected: {data["reason"]}')
            self.in_game = False

        @self.sio.on('match_ended')
        def on_match_ended(data):
            print(f'Match ended. Winner: {data["winner"]}')
            self.in_game = False

        @self.sio.on('error')
        def on_error(data):
            print(f'Error: {data["message"]}')

    def connect(self, server_url='http://localhost:5000'):
        """Connect to multiplayer server"""
        if not SOCKETIO_AVAILABLE:
            print("Cannot connect: python-socketio not installed")
            return False

        try:
            self.sio.connect(server_url)
            return True
        except Exception as e:
            print(f'Failed to connect to server: {e}')
            return False

    def disconnect(self):
        """Disconnect from server"""
        if self.sio and self.connected:
            self.sio.disconnect()
            self.connected = False

    def find_match(self):
        """Start searching for a match"""
        if self.connected:
            self.sio.emit('find_match')

    def cancel_search(self):
        """Cancel matchmaking search"""
        if self.connected:
            self.sio.emit('cancel_search')

    def ready(self):
        """Mark player as ready"""
        if self.connected and self.in_game:
            self.sio.emit('ready')

    def send_unit_spawn(self, unit_type):
        """Send unit spawn event"""
        if self.connected and self.in_game:
            self.sio.emit('unit_spawn', {'unit_type': unit_type})

    def send_spell_cast(self, spell_name):
        """Send spell cast event"""
        if self.connected and self.in_game:
            self.sio.emit('spell_cast', {'spell_name': spell_name})

    def send_mine_built(self):
        """Send mine built event"""
        if self.connected and self.in_game:
            self.sio.emit('mine_built', {})

    def send_castle_damage(self, damage, new_hp):
        """Send castle damage event"""
        if self.connected and self.in_game:
            self.sio.emit('castle_damage', {
                'damage': damage,
                'new_hp': new_hp
            })

    def send_game_over(self, winner, reason='Castle destroyed'):
        """Send game over event"""
        if self.connected and self.in_game:
            self.sio.emit('game_over', {
                'winner': winner,
                'reason': reason
            })

    def get_opponent_actions(self):
        """Get and clear opponent actions queue"""
        actions = self.opponent_actions.copy()
        self.opponent_actions.clear()
        return actions

    def is_player1(self):
        """Check if this player is player 1"""
        return self.role == 'player1'

    def is_player2(self):
        """Check if this player is player 2"""
        return self.role == 'player2'
