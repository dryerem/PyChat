import os
import configparser

from server import Server


def main():
    # path's
    root_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(root_path, 'config.ini')
    
    # config
    config = configparser.ConfigParser()
    config.read(config_path)

    host = config["Server"]["host"]
    port = int(config["Server"]["port"])

    server = Server(host=host, port=port, debug=True)
    server.run()

if __name__ == '__main__':
    main()