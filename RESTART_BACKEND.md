# How to Restart Backend Server

## Quick Fix for Media Transcription 404 Errors

The media transcription routes are correctly implemented, but the backend server needs to be **restarted** to load them.

## Steps to Restart Backend

### Option 1: If Backend is Running in a Terminal

1. **Find the terminal window** where the backend is running
2. **Stop the server**: Press `Ctrl+C` in that terminal
3. **Restart the server**:
   ```bash
   cd backend
   python run_server.py
   ```
   Or if using uvicorn directly:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

### Option 2: If Backend is Running as a Background Process

1. **Find and kill the process**:
   ```powershell
   # Find process on port 8000
   netstat -ano | findstr :8000
   
   # Kill the process (replace PID with the number from above)
   taskkill /PID <PID> /F
   ```

2. **Restart the server**:
   ```bash
   cd backend
   python run_server.py
   ```

### Option 3: Using PowerShell Script

Create a file `restart-backend.ps1`:
```powershell
# Stop any process on port 8000
$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($process) {
    $pid = $process.OwningProcess
    Stop-Process -Id $pid -Force
    Write-Host "Stopped process $pid on port 8000"
}

# Wait a moment
Start-Sleep -Seconds 2

# Start backend
Write-Host "Starting backend server..."
cd backend
python run_server.py
```

## Verify Routes Are Loaded

After restarting, verify the routes are available:

1. **Check FastAPI docs**: Open http://localhost:8000/docs
   - Look for "media-transcription" section
   - You should see:
     - `GET /api/media/health`
     - `POST /api/media/youtube/transcribe`

2. **Run test script**:
   ```bash
   cd backend
   python test_media_routes.py
   ```
   This will verify routes are registered.

3. **Check server logs**: Look for:
   ```
   Media transcription router initialized with prefix: /api/media
   Media transcription routes registered: ['/api/media/health', '/api/media/youtube/transcribe']
   ```

## Install Missing Dependencies

If you see import errors, install required packages:

```bash
cd backend
pip install yt-dlp
```

Or if using virtual environment:
```bash
cd backend
..\aigov_env\Scripts\pip.exe install yt-dlp
```

## Troubleshooting

### Routes Still Not Appearing

1. **Check for import errors** in server startup logs
2. **Verify router is imported** in `backend/app/main.py`:
   ```python
   from app.api import media_transcription
   app.include_router(media_transcription.router, tags=["media-transcription"])
   ```
3. **Run test script**: `python backend/test_media_routes.py`
4. **Check server logs** for any errors during startup

### Still Getting 404 After Restart

1. **Clear browser cache** and hard refresh (Ctrl+Shift+R)
2. **Check Vite proxy** is working - requests to `/api/*` should go to `http://localhost:8000`
3. **Test directly**: Try `http://localhost:8000/api/media/health` in browser (will need auth token)
4. **Check CORS** settings allow requests from frontend

## Expected Behavior After Restart

- ✅ Routes appear in http://localhost:8000/docs
- ✅ Health endpoint returns status (with auth)
- ✅ Frontend can call `/api/media/health` and `/api/media/youtube/transcribe`
- ✅ No 404 errors in browser console

