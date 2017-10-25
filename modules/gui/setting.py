import pickle


class Setting:
    def __init__(self):
        self.w = 1280
        self.h = 720

    def load(self, filename):
        try:
            file = open(filename, 'r')
            self.__dict__.update(pickle.load(file).__dict__)
        finally:
            file.close()

    def save(self, filename):
        try:
            file = open(filename, 'w')
            pickle.dump(self, file)
        finally:
            file.close()

    def set_to_window(self, window):
        raise NotImplementedError

    def get_from_window(self, window):
        raise NotImplementedError
