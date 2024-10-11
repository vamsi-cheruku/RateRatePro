import unittest
from enum import Enum

import requests


class Url(Enum):
    TEST_SETUP_BASE_URL = "http://127.0.0.1:8000/v1/"
    AWS_BASE_URL = "http://54.174.1.36:8000/v1/"
    USER_CREATE = "user/create"
    USER_FETCH = "user/fetch"
    
class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.url = Url.TEST_SETUP_BASE_URL

    def test_create_user(self):
        data = {
            "name": "John Doe",
            "nickname": "jd",
            "major": "Computer Science",
            "email": "johndoe@gmail.com",
            "password": "password123"
        }
        url = str(self.url)+ str(Url.USER_CREATE)
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 201)

    def test_fetch_user(self):
        userid = 1
        url = str(self.url) + "user/fetch/?userid=" +  str(userid)
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        
if __name__ == "__main__":
    unittest.main()