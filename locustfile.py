import json
from locust import HttpUser, task, between


class StudyChatUser(HttpUser):

    host = "http://127.0.0.1:8000"

    wait_time = between(1, 3)

    @task
    def ask_question(self):

        self.client.post(
            "/api/chat/study/",
            data=json.dumps({
                "query": "What is a Binary Search Tree?"
            }),
            headers={
                "Content-Type": "application/json"
            }
        )