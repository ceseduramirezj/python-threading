import requests

from queue import Empty
from lxml import html
import threading
import datetime
import random
import time

#Se puede crear una clase que hereda de Thread de esta forma a la hora de crear una instancia de esta clas
#se inicia un hilo que ejecuta la funcion que hayamos especificado, tambien indicamos los parametros necesarios
#en el constructor. Esta clase permite configurar y ejecutar todas las funciones y atributos de la clase Thread.

class YahooFinancePriceScheduler(threading.Thread):

    def __init__(self, input_queue, output_queues, **kwargs):
        super(YahooFinancePriceScheduler, self).__init__(**kwargs)
        self._input_queue = input_queue
        temp_queue = output_queues
        if not isinstance(temp_queue, list):
            temp_queue = [temp_queue]
        self._output_queues = output_queues
        self.start()

    def run(self):
        while(True):
            try:
                val = self._input_queue.get(timeout= 10)
            except Empty:
                print('Yahoo scheduler queu is empty, stopping')
                break

            if val == 'DONE':
                for output_queue in self._output_queues:
                    output_queue.put('DONE')
                break
            
            yahooFinancePriceWorker = YahooFinancePriceWorker(symbol=val)
            price = yahooFinancePriceWorker.get_price()

            for output_queue in self._output_queues:
                output_values = (val, price, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                output_queue.put(output_values)

            time.sleep(random.random())

            """ for output_queue in self._output_queues:
                for i in range(20):
                    output_queue.put('DONE') """

class YahooFinancePriceWorker():

    def __init__(self, symbol):
        self._symbol = symbol
        self._url = f'https://finance.yahoo.com/quote/{self._symbol}'

    def get_price(self):

        response = requests.get(self._url)

        if response.status_code != 200:
            print("Couldn't get entries")
            return

        page_contents = html.fromstring(response.text)
        raw_price = page_contents.xpath('//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section[1]/div[1]/fin-streamer[1]/span')[0].text
        price = float(raw_price.replace(',', ''))
        return price