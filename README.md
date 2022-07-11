
# Audiophile

A service that stores information about audio files, provides access to this information and periodically updates this data with updates from an included deep learning model.


## API Reference

#### Get all audio files

```
  GET /api/files
```

#### Get audio file

```
  GET /api/files/${file_id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. The ID of file to fetch |


```
  POST /api/files/upload
```
Uploads a file to the local media directory

| Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `file`      | `binary` | **Required**. The audio file to be uploaded |

```
  POST /api/files/upload/s3
```
Uploads a file to an S3 bucket

| Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `file`      | `binary` | **Required**. The audio file to be uploaded |

## Authors

- [@f-gozie](https://www.github.com/f-gozie)


## Demo

https://www.github.com/f-gozie
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

#### Mandatory .env Variables
`BASE_URL`: defaults to http://localhost:8000 if not specified

#### Optional .env variables (if you want to upload to s3 instead of locally)
`AWS_ACCESS_KEY_ID`

`AWS_SECRET_ACCESS_KEY`

`AWS_REGION`

`AWS_S3_BUCKET`

`S3_BUCKET_URL`


## Run Locally (Without Docker)

Clone the project

```bash
  git clone https://github.com/f-gozie/audiophile
```

Go to the project directory

```bash
  cd audiophile
```

Activate preferred virtual environment

```bash
  conda activate audiophile
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  uvicorn audiophile.main:app --reload
```

## Run Locally (With Docker)

Clone the project

```bash
  git clone https://github.com/f-gozie/audiophile
```

Go to the project directory

```bash
  cd audiophile
```

Build docker image using Dockerfile

```bash
  docker build -t audiophile .
```

Create a volume to persist DB

```bash
  docker volume create audiophile-db
```

Start the server

```bash
  docker run -p 8000:8000 --env-file=.env -v audiophile-db:/app audiophile
```
## Appendix

Any additional information goes here

For the `Prediction` model, the `reference` field on them is basically used to retrieve the latest predictions for a particular file. Whenever new predictions are generated (every 2 minutes), we create a new reference and update the file with the latest reference, and all newly generated predictions have the same reference. So when getting a file's detail, we filter the predictions by the reference on the file whic returns the latest predictions for the file.

Audio files can be added on demand by uploading them using the `/api/files/upload` endpoint. There is also an option to upload to an S3 bucket, but the default is to upload locally (since the code solution should be local and easy to run)

For the ability to have multiple models to run inferences against, we have a `models` class where we can add our models, and we group the models together which we use when running inferences. We run each phrase/utterance against each model and store the model information with the prediction that was generated.
