import time

class RevokedTokens:
    def __init__(self):
        self.data = {}

    def add(self, item):
        self.data[item] = time.time() + 86400 # one day expiry

    def remove_expired(self):
        now = time.time()
        expired = [k for k, v in self.data.items() if v <= now]
        for item in expired:
            del self.data[item]

    def __contains__(self, item):
        self.remove_expired()
        return item in self.data

    def __len__(self):
        self.remove_expired()
        return len(self.data)

    def __iter__(self):
        self.remove_expired()
        return iter(self.data)




