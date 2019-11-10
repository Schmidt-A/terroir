import os


def write_isolated_file(file_name, data):
    os.makedirs(os.path.dirname(file_name))
    with open(file_name, 'w+') as f:
        if type(data) == list:
            f.writelines(data)
        else:
            f.write(data)

class MockResponse(object):
    def __init__(self, html, url):
        self.text = html
        self.url = url