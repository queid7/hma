import pickle


def read_pickle(filename):
    file = open(filename, 'rb')
    data = pickle.load(file)
    file.close()
    return data


def write_pickle(filename, data):
    file = open(filename, 'wb')
    pickle.dump(data, file)
    file.close()
