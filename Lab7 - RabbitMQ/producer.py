import pika
from web_crawler import parse

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'queue'

def get_urls(max_page = 1):
    start_page = 1
    start_url = 'https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1='
    urls = parse(start_url, start_page, max_page)

    return urls


def main(urls):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)

    for url in urls:
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=url)

    print(" [x] Sent all URLs to queue.")

    connection.close()

if __name__ == "__main__":
    urls = get_urls(2)
    main(urls)