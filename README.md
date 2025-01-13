# pixel-chunk
A collaborative pixel art app backed by icechunk

Try it out at [pixel-chunk.fly.dev](https://pixel-chunk.fly.dev)

### What is this?

`pixel-chunks` is collaborative pixel art app, that allows users to draw on a shared canvas using transactional editing. 

### Why?

At [earthmover](https://earthmover.io) I have been working on a new cloud-native storage engine for zarr called [icechunk](https://icechunk.io). One of my favorite features of `icechunk` is that it requires no database to be runnning other than an object store like `s3`, while still offering consistency with transactions and versioning. I wanted to build a simple app that demonstrates the power of `icechunk` running on a serverless platform like `fly.io`. 

### The Stack

Backend:

- Python
- icechunk
- FastAPI
- Websockets
- Tigris
- Fly.io

Frontend:

- Typescript
- React
- Vite

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
# start the backend
uv run fastapi dev pixel_chunk/app.py
```

### Deploy on `fly`

```bash
# deploy the full stack
fly deploy
```

## License

This project is [MIT](./LICENSE) licensed.