# Get Random Dog API

A simple FastAPI application that fetches random dog images from [random.dog](https://random.dog) API.

## Features

- **GET `/dog`** - Returns JSON with random dog image URL and file size
- **GET `/dog/redirect`** - Redirects directly to a random dog image (great for `<img>` tags)
- **GET `/health`** - Health check endpoint for monitoring
- **GET `/`** - Redirects to API documentation (Swagger UI)
- **GET `/docs`** - Interactive API documentation (Swagger UI)
- **GET `/redoc`** - Alternative API documentation (ReDoc)

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Build the image
docker build -t get-random-dog .

# Run the container
docker run -p 8000:8000 get-random-dog
```

## API Endpoints

### Get Random Dog (JSON)

```bash
curl http://localhost:8000/dog
```

Response:
```json
{
  "url": "https://random.dog/abc123.jpg",
  "file_size_bytes": 131600
}
```

### Get Random Dog (Redirect)

```bash
curl -L http://localhost:8000/dog/redirect
```
Redirects directly to the image URL. Use in HTML:
```html
<img src="https://your-domain.com/dog/redirect" alt="Random Dog" />
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "get-random-dog-api"
}
```

## Free Deployment Options

### 1. Render.com (Recommended) ⭐

**Free tier includes:** Custom subdomain, SSL, auto-deploy from GitHub

1. Push this repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - **Name**: `get-random-dog` (or your preferred name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: `Free`
6. Click "Create Web Service"

Your API will be available at: `https://get-random-dog.onrender.com` (or your chosen name)

### 2. Railway.app

**Free tier includes:** $5/month credit, custom domains

1. Go to [Railway](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repo
4. Railway auto-detects Dockerfile
5. Your API gets a subdomain like: `https://get-random-dog-production.up.railway.app`

### 3. Fly.io

**Free tier includes:** 3 shared-cpu-1x VMs, 160GB monthly transfer

1. Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/)
2. Run: `fly launch` (in project directory)
3. Configure and deploy: `fly deploy`
4. Your API gets: `https://get-random-dog.fly.dev`

### 4. Cloudflare Workers (via Workers AI / Pages Functions)

**Free tier includes:** 100,000 requests/day

For FastAPI, use Cloudflare Pages with a Python worker or adapt to Workers.

### 5. PythonAnywhere

**Free tier includes:** One web app at `yourusername.pythonanywhere.com`

1. Create account at [PythonAnywhere](https://www.pythonanywhere.com)
2. Upload files via "Files" tab
3. Configure web app (manual setup for FastAPI)
4. Your API at: `https://yourusername.pythonanywhere.com`

## Domain Options

Since you want `get-random-dog` in the domain:

| Platform | Your Domain Format |
|----------|-------------------|
| Render | `https://get-random-dog.onrender.com` |
| Railway | `https://get-random-dog.up.railway.app` |
| Fly.io | `https://get-random-dog.fly.dev` |
| PythonAnywhere | `https://yourusername.pythonanywhere.com` |

**Custom Domain**: All platforms support adding your own domain (e.g., `get-random-dog.com`) for free if you own it.

## Environment Variables

No environment variables required for basic operation. The app connects directly to `https://random.dog/woof.json`.

## Project Structure

```
get-random-dog/
├── main.py           # FastAPI application
├── requirements.txt  # Python dependencies
├── Dockerfile        # Multi-stage Docker build
└── README.md         # This file
```

## License

MIT License - Feel free to use and modify!

## Credits

- Dog images provided by [random.dog](https://random.dog)
- Built with [FastAPI](https://fastapi.tiangolo.com)