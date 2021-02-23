FROM python:3.9
COPY ./app /app
WORKDIR /app
RUN set -ex && \
    pip install -r requirements.txt
EXPOSE 8051
CMD streamlit run app.py
