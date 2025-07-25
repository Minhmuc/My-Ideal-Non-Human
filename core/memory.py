class ConversationBufferMemory:
    def __init__(self):
        self.history = []
        self.context = {}  
    def add(self, user: str, message: str):
        self.history.append({"user": user, "message": message})

    def get_history(self, n: int = 5):
        return self.history[-n:]

    def set_context(self, key, value):
        self.context[key] = value  

    def get_context(self, key, default=None):
        return self.context.get(key, default)
