
class Hehe(object):
    def __init__(self):
        print("创建")

    def __del__(self):
        print("xiaoshi")

if __name__ == "__main__":
    for x in range(10):
        print(x)
        hehe = Hehe()
