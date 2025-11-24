# ngrok Setup Guide for External Testing

## Quick Start

This guide helps you expose your local Vite development server to the internet using ngrok.

## Prerequisites

1. **Frontend dev server running** on port 5173
2. **Backend server running** on port 8000 (for API calls)
3. **ngrok installed** (see installation below)

## Step 1: Update Vite Config ✅

The `vite.config.ts` has been updated to allow external network access:
- `host: true` - Allows ngrok to access the server

## Step 2: Install ngrok

### Windows (PowerShell)
```powershell
# Download ngrok
# Go to: https://ngrok.com/download
# Or use Chocolatey:
choco install ngrok

# Or use Scoop:
scoop install ngrok
```

### Manual Installation
1. Download from: https://ngrok.com/download
2. Extract to a folder (e.g., `C:\ngrok`)
3. Add to PATH or use full path

## Step 3: Authenticate ngrok (First Time Only)

```powershell
# Sign up at https://dashboard.ngrok.com/signup (free)
# Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

## Step 4: Start Frontend Dev Server

In one terminal:
```powershell
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

## Step 5: Start Backend Server (Required for API)

In another terminal:
```powershell
cd backend
python run_server.py
```

Or with Docker:
```powershell
docker-compose up backend
```

## Step 6: Start ngrok Tunnel

In a third terminal:
```powershell
ngrok http 5173
```

You'll see output like:
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5173
```

## Step 7: Share the Public URL

The **Forwarding** URL (e.g., `https://abc123.ngrok-free.app`) is your public link.

**Important Notes:**
- ⚠️ The frontend will try to call `/api` endpoints
- The API proxy in vite.config.ts points to `localhost:8000`
- External users won't be able to access the backend API through ngrok
- For full-stack testing, you need to either:
  1. **Option A**: Expose backend separately with another ngrok tunnel on port 8000
  2. **Option B**: Update vite.config.ts proxy to point to the backend ngrok URL

## Option A: Expose Backend Separately

```powershell
# In a 4th terminal
ngrok http 8000
```

Then update `frontend/vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'https://your-backend-ngrok-url.ngrok-free.app',
    changeOrigin: true,
  },
}
```

## Option B: Use ngrok's Static Domain (Paid Feature)

If you have ngrok Pro, you can use a static domain for the backend.

## Troubleshooting

### ngrok not found
- Make sure ngrok is in your PATH
- Or use full path: `C:\path\to\ngrok.exe http 5173`

### Connection refused
- Make sure Vite dev server is running
- Check that `host: true` is set in vite.config.ts
- Verify port 5173 is not blocked by firewall

### API calls fail
- Backend must be accessible
- Use Option A above to expose backend separately
- Or test with backend running locally and share both URLs

### ngrok free tier limitations
- URLs change on each restart
- Limited connections per minute
- For production testing, consider ngrok paid plans

## Security Warning

⚠️ **ngrok URLs are public and temporary**
- Anyone with the URL can access your app
- Stop ngrok when done testing
- Don't share URLs publicly
- Use ngrok's authentication features for sensitive apps

## Quick Commands Summary

```powershell
# Terminal 1: Frontend
cd frontend
npm run dev

# Terminal 2: Backend
cd backend
python run_server.py

# Terminal 3: ngrok (Frontend)
ngrok http 5173

# Terminal 4: ngrok (Backend - Optional)
ngrok http 8000
```

## Next Steps

1. ✅ Vite config updated
2. Install ngrok
3. Authenticate ngrok
4. Start frontend dev server
5. Start backend server
6. Start ngrok tunnel
7. Share the public URL

