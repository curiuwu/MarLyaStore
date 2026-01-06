FROM python:3.12-slim


WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_KEY='PWPUSH_MASTER_KEY=7725175e0483c14dda509f8cd5032175554f085924a487e3b61f4364a713a4c2'
ENV SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://market_user:12345@62.60.216.29:5432/marketplace?sslmode=disable"
ENV SQLALCHEMY_TRACK_MODIFICATIONS=False

EXPOSE 8080
CMD ["python", "run.py"]
