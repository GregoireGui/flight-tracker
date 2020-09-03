from flight import flight_tracking
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler

def main():
    apps = {'/': Application(FunctionHandler(flight_tracking))}
    server = Server(apps, port=8084)
    server.start()
    server.io_loop.start()

if __name__ == "__main__":
    main()