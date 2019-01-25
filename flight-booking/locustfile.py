import os
from locust import HttpLocust, TaskSet


def login(l):
    l.client.post('/api/v2/accounts/auth_user/',
                  {
                      'username': os.getenv('LOCUST_USER', default='user'),
                      'password': os.getenv('LOCUST_PASS', default='password')
                  })


def get_reservations(l):
    l.client.get("/api/v1/reservations/")


class UserBehavior(TaskSet):
    tasks = {get_reservations: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
