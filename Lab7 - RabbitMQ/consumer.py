from time import sleep
from tinydb import TinyDB
from data_crawler import parse
import pika, threading

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'queue'

class Consumer:
    def __init__(self, db, lock):
        self.db = db
        self.lock = lock

    def callback(self, ch, method, properties, body):
        url = body.decode('utf-8')
        sleep(3)

        data = parse(url)
        try:
            if data is not None:
                with self.lock:
                    self.db.insert(data)
                print(f" [x] ({threading.current_thread().name}) Received URL: {url}")
        except Exception as e:
            print(f"Error: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_thread(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()

        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=self.callback)

        print(f" [*] ({threading.current_thread().name}) Consumer is waiting for messages. To exit press CTRL+C")
        channel.start_consuming()

def main(file_name, threads_num):
    db = TinyDB(f'{file_name}', encoding='utf-8')
    lock = threading.Lock()
    consumer = Consumer(db, lock)

    threads = []

    for i in range(threads_num):
        thread = threading.Thread(target=consumer.start_thread, name=f"ConsumerThread-{i}")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    file_name = "database.json"
    num_consumers = 20

    main(file_name, num_consumers)