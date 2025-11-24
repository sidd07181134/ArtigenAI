# Media Transcription Setup & Troubleshooting

## Issue: 404 Errors on `/api/media/health` and `/api/media/youtube/transcribe`

### Root Cause
The backend server needs to be **restarted** to load the new media transcription routes.

### Solution

1. **Install yt-dlp dependency** (if not already installed):
   ```bash
   cd backend
   pip install yt-dlp
   ```
   Or if using a virtual environment:
   ```bash
   cd backend
   ..\aigov_env\Scripts\pip.exe install yt-dlp
   ```

2. **Restart the backend server**:
   - Stop the current backend server (Ctrl+C in the terminal where it's running)
   - Restart it:
     ```bash
     cd backend
     python run_server.py
     ```
     Or if using uvicorn directly:
     ```bash
     cd backend
     uvicorn app.main:app --reload --port 8000
     ```

3. **Verify routes are registered**:
   - Open http://localhost:8000/docs in your browser
   - Look for "media-transcription" section
   - You should see:
     - `POST /api/media/youtube/transcribe`
     - `GET /api/media/health`

### Expected Routes

After restart, these routes should be available:
- `GET /api/media/health` - Health check endpoint
- `POST /api/media/youtube/transcribe` - Transcribe YouTube video

### Frontend Configuration

The frontend is correctly configured:
- API base URL: `/api` (proxied to `http://localhost:8000` via Vite)
- Routes:
  - `GET /api/media/health` → `http://localhost:8000/api/media/health`
  - `POST /api/media/youtube/transcribe` → `http://localhost:8000/api/media/youtube/transcribe`

### Verification Steps

1. **Check backend is running**:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 8000
   ```

2. **Test health endpoint directly**:
   ```powershell
   curl http://localhost:8000/api/media/health
   ```
   (You'll need to be authenticated - use the admin token)

3. **Check FastAPI docs**:
   - Open http://localhost:8000/docs
   - Look for "media-transcription" tag
   - Try the endpoints from the Swagger UI

### Common Issues

1. **ModuleNotFoundError: No module named 'yt_dlp'**
   - Solution: Install yt-dlp (see step 1 above)
   - Note: The router will still load, but transcription will fail with a clear error message

2. **404 Not Found after restart**
   - Check that the router is imported in `backend/app/main.py`
   - Check that `app.include_router(media_transcription.router)` is called
   - Verify no import errors in backend logs

3. **Vite proxy not working**
   - Check `frontend/vite.config.ts` has proxy configuration for `/api`
   - Restart the frontend dev server if you changed vite.config.ts

### Files Modified

- `backend/requirements.txt` - Added yt-dlp
- `backend/app/services/media_transcription_service.py` - YouTube transcription service
- `backend/app/api/media_transcription.py` - API endpoints
- `backend/app/models/schemas.py` - Request/response models
- `backend/app/main.py` - Router registration
- `frontend/src/services/api.ts` - API client methods
- `frontend/src/pages/Admin/Dashboard/MediaTranscription.tsx` - UI component
- `frontend/src/App.tsx` - Route and navigation

