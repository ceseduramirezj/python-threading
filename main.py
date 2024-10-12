import time
import os

from yaml_reader import YamlPipelineExecutor

#Concurrencia
#La ejecucion de hilos se realiza en un solo nucleo, es decir que un hilo es ejecutado en tiempos separados mientras
#otros hilos esperan a su turno. Pensemos en un juego de mesa en el que para que cada jugador avance una casilla,
#necesita que sea su turno. Es asi como se reparte el trabajo por trozos.
#A la hora de hacer un join de un hilo, volviendo al ejemplo del juego de mesa el hilo correspondiente tendria
#que terminar el juego mientras los otros jugadores esperan a que termine y puedan reanudar al juego normal en el que
#a cada uno le toca su turno cuando termina del otro

def main():
    scraper_start_time = time.time()

    pipeline_location = os.environ.get('PIPELINE_LOCATION')

    yaml_pipeline_executor = YamlPipelineExecutor(pipeline_location= pipeline_location)
    yaml_pipeline_executor.start()
    yaml_pipeline_executor.join()

    print('Extracting time took:', round(time.time() - scraper_start_time, 1))

if __name__ == "__main__":
    main()