import threading

import requests
from bs4 import BeautifulSoup

class WikiWorkerMasterScheduler(threading.Thread):

    def __init__(self, output_queues, **kwargs):
        if 'input_queue' in kwargs:
            kwargs.pop('input_queue')

        self._input_values = kwargs.pop('input_values')

        temp_queue = output_queues
        if not isinstance(temp_queue, list):
            temp_queue = [temp_queue]
        self._output_queues = output_queues

        super(WikiWorkerMasterScheduler, self).__init__(**kwargs)
        self.start()

    def run(self):
        for entry in self._input_values:
            wiki_worker = WikiWorker(entry)

            symbol_counter = 0
            for symbol in wiki_worker.get_sp_500_companies():
                for output_queue in self._output_queues:
                    output_queue.put(symbol)
                symbol_counter += 1
                if symbol_counter >= 5:
                    break

        """ for output_queue in self._output_queues:
            for i in range(20):
                output_queue.put('DONE') """


class WikiWorker():

    def __init__(self, url):
        self._url = url

    @staticmethod
    def _extract_company_symbols(page_html):
        soup = BeautifulSoup(page_html, 'lxml')

        table = soup.find(id= 'constituents')
        table_rows = table.find_all('tr')

        for table_row in table_rows[1:]:
            symbol = table_row.find('td').text.strip('\n')
            yield symbol

    def get_sp_500_companies(self):
        response = requests.get(self._url)

        if response.status_code != 200:
            print("Couldn't get entries")
            return []
        
        yield from self._extract_company_symbols(response.text)
        