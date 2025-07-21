
class ConversationBufferMemory:
    """
    Lưu trữ lịch sử hội thoại đơn giản trong bộ nhớ tạm.
    """
    def __init__(self):
        self.history = []

    def add(self, user: str, message: str):
        self.history.append({"user": user, "message": message})

    def get_history(self, n: int = 5):
        """Lấy n lượt hội thoại gần nhất."""
        return self.history[-n:]

    def clear(self):
        self.history = []