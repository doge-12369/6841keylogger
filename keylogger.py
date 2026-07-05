import keyboard

def key_callback(event : keyboard.KeyboardEvent):
    print(event.name)

def main():
    print("hello world")
    keyboard.hook(key_callback)
    keyboard.wait()

if __name__ == "__main__":
    main()