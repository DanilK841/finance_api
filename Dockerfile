FROM python:3.13.7

WORKDIR /app

COPY req.txt req.txt

RUN pip install --upgrade pip
RUN pip install -r req.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
