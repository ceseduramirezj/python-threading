from sqlalchemy import create_engine, text, URL

from queue import Empty
import threading
import os

class PostgresMasterScheduler(threading.Thread):

    def __init__(self, input_queue, **kwargs):
        if 'output_queues' in kwargs:
            kwargs.pop('output_queues')
        super(PostgresMasterScheduler, self).__init__(**kwargs)
        self._input_queue = input_queue
        self.start()

    def run(self):
        while True:
            try:
                val = self._input_queue.get(timeout=10)
            except Empty:
                print('Timeout reached in postgres scheduler, stopping')
                break
                
            if val == 'DONE':
                break
            print('Received:', val)
            symbol, price, extracted_time = val
            postgresWorker = PostgresWorker(symbol, price, extracted_time)
            postgresWorker.insert_into_db()

class PostgresWorker():
    def __init__(self, symbol, price, extracted_time):
        self._symbol = symbol
        self._price = price
        self._extracted_time = extracted_time

        self._DB_USER = os.environ.get('DB_USER')
        self._DB_PWD = os.environ.get('DB_PWD')
        self._DB_HOST = os.environ.get('DB_HOST')
        self._DB_PORT = os.environ.get('DB_PORT')
        self._DB_NAME = os.environ.get('DB_NAME')

        self._url_obj = URL.create(
            "postgresql+psycopg2",
            username=self._DB_USER,
            password=self._DB_PWD,
            host=self._DB_HOST,
            port=self._DB_PORT,
            database=self._DB_NAME,
        )
        self._engine = create_engine(self._url_obj, echo=False, client_encoding="utf8")

    def _create_insert_sql(self):
        SQL = """INSERT INTO public.prices (symbol, price, extracted_time) VALUES (:symbol, :price, :extracted_time)"""
        return SQL

    def insert_into_db(self):
        insert_query = self._create_insert_sql()

        with self._engine.connect() as conn:
            params = {"symbol": self._symbol,
                    "price": self._price,
                    "extracted_time": self._extracted_time}
            print(params)
            conn.execute(text(insert_query), params)
            conn.commit()