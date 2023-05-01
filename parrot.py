# coding=utf-8
"""
05/01/2023

"""


def main():
    while True:
        try:
            inp = input("👂: ")
            print("🦜:" + inp)
        except Exception as e:
            raise e
        except KeyboardInterrupt:
            print("\n👋")
        finally:
            exit()


if __name__ == '__main__':
    main()
