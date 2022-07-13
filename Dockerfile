FROM python:3.10

WORKDIR /app

COPY ./docker-requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN pip install torch==1.12.0+cpu torchaudio==0.12.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY ./audiophile /app/audiophile

#CMD ["uvicorn", "audiophile.main:app", "--host", "0.0.0.0", "--port", "8000"]
