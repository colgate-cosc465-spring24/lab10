#!/usr/bin/python3

from argparse import ArgumentParser
import logging
import sliding_window
import time

def main():
    # Parse arguments
    arg_parser = ArgumentParser(description='Server', add_help=False)
    arg_parser.add_argument('-p', '--port', dest='port', action='store',
            type=int, required=True, help='Local port')
    arg_parser.add_argument('-h', '--hostname', dest='hostname', action='store',
            type=str, default='', help='Local hostname')
    arg_parser.add_argument('-b', '--buffer', dest='buffer_size', 
            action='store', type=int, default=5, help='Buffer_size')
    arg_parser.add_argument('-l', '--loss', dest='loss_probability', 
            action='store', type=float, default=0.0, help='Loss probability')
    arg_parser.add_argument('-c', '--consumption', dest='consumption_interval', 
            action='store', type=float, default=0.0, help='Consumption internval (in seconds); 0 means consume immediately')
    settings = arg_parser.parse_args()

    logging.basicConfig(level=logging.DEBUG, 
            format='%(levelname)s: %(message)s')

    receiver = sliding_window.Receiver((settings.hostname, settings.port), 
            settings.buffer_size, settings.loss_probability)
    while True:
        time.sleep(settings.consumption_interval)
        data = receiver.recv().decode()
        print('%s' % data)

if __name__ == '__main__':
    main()
