# pixel-chunk
A collaborative pixel art app backed by icechunk

## Run Locally

```bash
# build the frontend
cd frontend
npm run build

# start the backend
uv run fastapi dev pixel_chunk/app.py
```

## Deploy on `fly`

```bash
# build the frontend
cd frontend
npm run build

# deploy the full stack
fly deploy
```
