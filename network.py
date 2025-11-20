"""
Network Manager for Multiplayer
Handles client-server communication for both desktop and web
"""

import sys
import json

# Detect platform
IS_WEB = sys.platform == 'emscripten' or 'pygbag' in sys.modules

# Try to import platform for web access
if IS_WEB:
    try:
        import platform
        JS_AVAILABLE = hasattr(platform, 'window')
    except:
        JS_AVAILABLE = False
else:
    JS_AVAILABLE = False

# Try to import socketio for desktop
if not IS_WEB:
    try:
        import socketio
        SOCKETIO_AVAILABLE = True
    except ImportError:
        SOCKETIO_AVAILABLE = False
        print("Warning: python-socketio not available. Multiplayer disabled.")
else:
    SOCKETIO_AVAILABLE = False


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

        # Web-specific
        self.is_web = IS_WEB
        self.js_ws = None

        print(f"[Network] Platform: {'Web' if IS_WEB else 'Desktop'}")
        print(f"[Network] SocketIO: {SOCKETIO_AVAILABLE}, JS: {JS_AVAILABLE}")

        if not IS_WEB and SOCKETIO_AVAILABLE:
            # Desktop mode
            self.sio = socketio.Client()
            self.setup_desktop_handlers()
        elif IS_WEB and JS_AVAILABLE:
            # Web mode
            try:
                import platform as plat
                self.js_ws = plat.window.gameWebSocket
                print("[Network] Web mode: JavaScript WebSocket bridge ready")
            except Exception as e:
                print(f"[Network] Failed to access JavaScript bridge: {e}")

    def setup_desktop_handlers(self):
        """Setup event handlers for desktop (python-socketio)"""
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

    def poll_web_messages(self):
        """Poll messages from JavaScript WebSocket (web mode)"""
        if not self.is_web or not self.js_ws:
            return

        try:
            import platform as plat
            messages = plat.window.gameWebSocket.getMessages()

            if messages and len(messages) > 0:
                for msg in messages:
                    msg_type = msg.get('type')

                    if msg_type == 'connected':
                        self.player_id = msg.get('player_id')
                        self.connected = True
                        print(f'[Web] Connected: {self.player_id}')

                    elif msg_type == 'match_found':
                        self.game_id = msg.get('game_id')
                        self.role = msg.get('role')
                        self.in_game = True
                        print(f'[Web] Match found! Role: {self.role}')

                    elif msg_type == 'game_start':
                        print('[Web] Game starting!')

                    elif msg_type == 'opponent_unit_spawn':
                        self.opponent_actions.append({
                            'type': 'unit_spawn',
                            'unit_type': msg.get('unit_type')
                        })

                    elif msg_type == 'opponent_spell_cast':
                        self.opponent_actions.append({
                            'type': 'spell_cast',
                            'spell_name': msg.get('spell_name')
                        })

                    elif msg_type == 'opponent_mine_built':
                        self.opponent_actions.append({
                            'type': 'mine_built',
                            'mines': msg.get('mines', 0)
                        })

                    elif msg_type == 'disconnected':
                        self.connected = False
                        self.in_game = False

        except Exception as e:
            print(f'[Web] Poll error: {e}')

    def connect(self, server_url='http://localhost:5000'):
        """Connect to multiplayer server"""
        print(f"[Network] Connecting to: {server_url}")

        if self.is_web and self.js_ws:
            # Web mode - use JavaScript WebSocket
            try:
                import platform as plat
                result = plat.window.gameWebSocket.connect(server_url)
                self.connected = True
                print(f"[Web] Connect result: {result}")
                return True
            except Exception as e:
                print(f"[Web] Connect failed: {e}")
                return False

        elif not self.is_web and SOCKETIO_AVAILABLE:
            # Desktop mode - use python-socketio
            try:
                self.sio.connect(server_url)
                return True
            except Exception as e:
                print(f'[Desktop] Connect failed: {e}')
                return False

        return False

    def disconnect(self):
        """Disconnect from server"""
        if self.is_web and self.js_ws:
            try:
                import platform as plat
                plat.window.gameWebSocket.disconnect()
            except:
                pass
        elif self.sio and self.connected:
            self.sio.disconnect()

        self.connected = False

    def send_message(self, event_name, data=None):
        """Send a message to server"""
        if data is None:
            data = {}

        message = {
            'event': event_name,
            'data': data
        }

        if self.is_web and self.js_ws:
            try:
                import platform as plat
                plat.window.gameWebSocket.send(message)
                return True
            except Exception as e:
                print(f'[Web] Send failed: {e}')
                return False

        elif self.sio and self.connected:
            try:
                self.sio.emit(event_name, data)
                return True
            except Exception as e:
                print(f'[Desktop] Send failed: {e}')
                return False

        return False

    def find_match(self):
        """Start searching for a match"""
        if self.connected:
            return self.send_message('find_match')
        return False

    def cancel_search(self):
        """Cancel matchmaking search"""
        if self.connected:
            return self.send_message('cancel_search')
        return False

    def ready(self):
        """Mark player as ready"""
        if self.connected and self.in_game:
            return self.send_message('ready')
        return False

    def send_unit_spawn(self, unit_type):
        """Send unit spawn event"""
        if self.connected and self.in_game:
            return self.send_message('unit_spawn', {'unit_type': unit_type})
        return False

    def send_spell_cast(self, spell_name):
        """Send spell cast event"""
        if self.connected and self.in_game:
            return self.send_message('spell_cast', {'spell_name': spell_name})
        return False

    def send_mine_built(self):
        """Send mine built event"""
        if self.connected and self.in_game:
            return self.send_message('mine_built', {})
        return False

    def send_game_over(self, winner, reason='Castle destroyed'):
        """Send game over event"""
        if self.connected and self.in_game:
            return self.send_message('game_over', {
                'winner': winner,
                'reason': reason
            })
        return False

    def get_opponent_actions(self):
        """Get and clear opponent actions queue"""
        # Poll for new messages in web mode
        if self.is_web:
            self.poll_web_messages()

        actions = self.opponent_actions.copy()
        self.opponent_actions.clear()
        return actions

    def is_player1(self):
        """Check if this player is player 1"""
        return self.role == 'player1'

    def is_player2(self):
        """Check if this player is player 2"""
        return self.role == 'player2'

    def is_available(self):
        """Check if multiplayer is available"""
        return (IS_WEB and JS_AVAILABLE) or (not IS_WEB and SOCKETIO_AVAILABLE)


# Export flag for game.py
MULTIPLAYER_AVAILABLE = IS_WEB or SOCKETIO_AVAILABLE
