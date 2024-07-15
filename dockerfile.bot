FROM python:3.11-alpine

RUN apk update && apk add --no-cache gcc musl-dev
RUN pip install --upgrade pip


RUN mkdir bot

COPY bot bot

RUN pip install -r bot/requirements.txt

WORKDIR bot

CMD ["python3","-u", "main.py"]