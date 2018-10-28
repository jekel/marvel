FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY . .
RUN pip3 install -r requirements.txt


ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

EXPOSE 5000
ENV KEY ''
ENV SECRET ''

CMD ["python", "main.py"]
