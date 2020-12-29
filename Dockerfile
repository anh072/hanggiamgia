FROM python:3.9-buster

ENV FLASK_APP patched.py
ENV FLASK_CONFIG production

RUN adduser app

WORKDIR /home/hanggiamgia

RUN chown app /home/hanggiamgia
USER app

COPY requirements.txt .
RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY manage.py config.py boot.sh patched.py ./

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]