FROM python:3.11.6
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./django-telegram-tagger .
EXPOSE 8000
RUN ls
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000", "--insecure", "--noreload", "--skip-checks"]
