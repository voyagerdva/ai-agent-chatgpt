#=== \core\SessionContext.py ================================

import uuid

class SessionContext:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.history = []
        self.turn_count = 0

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        self.turn_count += 1

    def get_history(self):
        return self.history

    def get_id(self):
        return self.session_id
