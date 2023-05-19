# Manifest Destiny

Flask API that processes a CSV into a filled out DA FORM 1306.

## Installation and Usage

### API

From the `docker` directory:

```
docker build --tag docker-app .
docker run -it -p 8000:8000 -d docker-app
```

Post a CSV to process:

```
curl -i -X POST -H "Content-Type: multipart/form-data" \
-F "file=@/sample_data.csv" \
http://0.0.0.0:8000/processfile
```

Download a filled out DA FORM 1306: http://0.0.0.0:8000/files/manifest.pdf

### Web App

From the `docker` directory:

```
docker build --tag docker-app .
docker run -it -p 5000:5000 -d docker-app
```

Access the web app: http://0.0.0.0:5000
