FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./audiophile /app/audiophile

CMD ["uvicorn", "audiophile.main:app", "--host", "0.0.0.0", "--port", "8000"]
