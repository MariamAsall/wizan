from locust import HttpUser, task, between
import json
import random


QUESTIONS = [
    "What is a Binary Search Tree?",
    "Explain Django ORM",
    "What is a Queue?",
    "What is a Stack?",
    "Explain REST API",
    "What is PostgreSQL?",
    "What is a linked list?",
]


class StudyChatUser(HttpUser):

    host = "http://127.0.0.1:8000"

    wait_time = between(1, 3)

    @task
    def ask_question(self):

        question = random.choice(QUESTIONS)

        self.client.post(
            "/api/chat/study/",
            data=json.dumps({
                "query": question
            }),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_ACCESS_TOKEN"
            }
        )