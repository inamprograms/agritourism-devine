class GuardrailsService:
    MAX_MESSAGE_LENGTH = 2000
    BLOCKED_WORDS = ["hack", "exploit", "jailbreak", "ignore previous instructions"]

    def validate(self, message: str):
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message too long. Maximum {self.MAX_MESSAGE_LENGTH} characters allowed")

        message_lower = message.lower()
        for word in self.BLOCKED_WORDS:
            if word in message_lower:
                raise ValueError("Message contains unsafe content")

        return True