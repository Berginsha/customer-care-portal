FROM python:3.9.16-slim
WORKDIR /app
COPY app app
COPY templates templates
COPY static static
COPY data.json .
COPY app.py .
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000
CMD [ "python3","app.py","dev" ]

