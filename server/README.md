# Castle Strategy Multiplayer Server

WebSocket server for Castle Strategy game multiplayer mode.

## Features

- Real-time matchmaking
- 1vs1 game rooms
- Action synchronization (units, spells, mines)
- Automatic cleanup on disconnect

## Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Server

```bash
python multiplayer_server.py
```

Server will run on `http://localhost:5000`

## Deployment

### Railway.app Deployment

1. **Create a Railway account** at [railway.app](https://railway.app)

2. **Create a new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository

3. **Configure the service**
   - Railway will auto-detect the Procfile
   - Set root directory to `server/`
   - Railway will automatically install dependencies from `requirements.txt`

4. **Get your server URL**
   - Railway will provide a public URL like: `https://your-app.railway.app`
   - Copy this URL to use in your game client

5. **Update game client**
   - In `game.py`, change `self.server_url` to your Railway URL:
   ```python
   self.server_url = 'https://your-app.railway.app'
   ```

### Environment Variables

No special environment variables required. The server uses:
- `PORT` - Automatically set by Railway

## API Endpoints

### HTTP Endpoints

- `GET /` - Health check, returns server status

### WebSocket Events

#### Client → Server

- `find_match` - Start matchmaking
- `cancel_search` - Cancel matchmaking
- `ready` - Mark player as ready
- `unit_spawn` - Notify opponent of unit spawn
- `spell_cast` - Notify opponent of spell cast
- `mine_built` - Notify opponent of mine construction
- `castle_damage` - Notify opponent of castle damage
- `game_over` - End the match
- `ping` - Latency check

#### Server → Client

- `connected` - Connection established
- `searching` - Searching for opponent
- `match_found` - Match found, includes game_id and role
- `game_start` - Both players ready
- `opponent_unit_spawn` - Opponent spawned a unit
- `opponent_spell_cast` - Opponent cast a spell
- `opponent_mine_built` - Opponent built a mine
- `castle_damaged` - Your castle was damaged
- `opponent_disconnected` - Opponent left
- `match_ended` - Match finished
- `error` - Error message
- `pong` - Latency response

## Monitoring

Check server status:
```bash
curl https://your-server-url.railway.app/
```

Response:
```json
{
  "status": "online",
  "active_games": 0,
  "waiting_players": 0
}
```

## Troubleshooting

### Server not responding
- Check Railway logs
- Ensure server is deployed correctly
- Verify PORT environment variable is set

### Players can't connect
- Check CORS settings (currently allows all origins)
- Verify firewall rules
- Check Railway service is running

### Matchmaking not working
- Check server logs for errors
- Verify WebSocket connection is established
- Test with `/` endpoint to ensure server is online

## Security Notes

**Production recommendations:**
1. Change `SECRET_KEY` in `multiplayer_server.py`
2. Restrict CORS to your game's domain
3. Add rate limiting
4. Implement authentication if needed
5. Add game state validation
6. Monitor for abuse

## Architecture

```
Client 1 ←→ WebSocket Server ←→ Client 2
             │
             ├─ Matchmaking Queue
             ├─ Active Games
             └─ Player Sockets
```

## License

Same as the main game project.
