import threading

class EmailThread(threading.Thread):
    def __init__(self, email_msg):
        super(EmailThread, self).__init__()
        self.email_msg = email_msg

    def run(self):
        self.email_msg.send()