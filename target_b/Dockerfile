FROM python:3.11-slim
WORKDIR /app

# copy server and files
COPY server.py /app/server.py
COPY files /app/files

# ensure secret is readable (so server can open it in general)
RUN chmod 644 /app/files/docs/secret.txt || true

EXPOSE 10991
CMD ["python", "server.py"]