import log

from app import App


def main():
    log.info('Instantiating the application...')
    app: App = App()

    log.info('Initializing the application...')
    app.init()

    log.info('Running the application...')
    app.run()


if __name__ == '__main__':
    main()
