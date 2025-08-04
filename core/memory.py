class ConversationBufferMemory:
    def __init__(self):
        self.history = []
        self.context = {}

    def add(self, role: str, message: str):
        # role: "user" hoặc "bot"
        self.history.append({"role": role, "message": message})

    def get_history(self, n: int = 5) -> str:
        recent = self.history[-n:]
        lines = []
        for turn in recent:
            prefix = "Người dùng" if turn["role"] == "user" else "Trợ lý"
            lines.append(f"{prefix}: {turn['message']}")
        return "\n".join(lines)

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key, default=None):
        return self.context.get(key, default)
