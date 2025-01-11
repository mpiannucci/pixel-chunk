# pixel-chunk
A collaborative pixel art app backed by icechunk

## Development

### Setup

Install the frontend dependencies

```bash
cd frontend
npm install
npm run build
```

Define the storage backend

```bash
export AWS_ACCESS_KEY_ID=myaccesskey
export AWS_ENDPOINT_URL_S3=myendpoitn
export AWS_REGION=auto
export AWS_SECRET_ACCESS_KEY=mysecretkey
export BUCKET_NAME=pixel-chunk
```

### Run Locally

```bash
# build the frontend
cd frontend
npm run build

# start the backend
uv run fastapi dev pixel_chunk/app.py
```

### Deploy on `fly`

```bash
# build the frontend
cd frontend
npm run build

# deploy the full stack
fly deploy
```
