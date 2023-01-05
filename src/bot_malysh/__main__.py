import bot_malysh

from bot_malysh import bot_listener as listener
def main():
    print(f'{bot_malysh.i_info}')
    listener.run()

if __name__ == "__main__":
    main()