import unittest
from unittest import mock
from originality import *
ACCOUNTS_PATH_TEST = "tests/testdata/accounts.txt"

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({"key1": "value1"}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)

def mocked_requests_post(*args, **kwargs):
    
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == f"{API_BASE_URL}/ai-plag":
        return MockResponse({
            "public_link": "http://someurl.com/test",
            "ai": {
                "score": {
                    "ai": 0.5
                }
            },
            "plagiarism": {
                "total_text_score": "50%"
            },
            "credits": 10
            }, 200)
    return MockResponse(None, 404)

class OriginalityTest(unittest.TestCase):

    def setUp(self) -> None:
        self.test_verdict_data = OriginalityVerdictData(
            "http://someurl.com/test",
            0.5,
            "50%"
        )
        self.test_account_data = OriginalityAccountData(
            "testname",
            "someemail@example.com",
            "testpassword",
            "testaccesstoken",
            20,
            "testapikey"
        )
        return super().setUp()
    
    @mock.patch('originality.requests.post', side_effect=mocked_requests_post)
    def test_verdict_get(self, mock_post):
        content = "testcontent"
        payload = {
            "content": content
        }
        headers = {
            'X-OAI-API-KEY': self.test_account_data.active_apikey
        }
        # test
        result = OriginalityVerdict.get(content, self.test_account_data)

        # assert the requests.post was called with the right arguments
        self.assertIn(mock.call(API_BASE_URL + "/ai-plag", headers=headers, json=payload), mock_post.call_args_list)
        self.assertEqual(result, self.test_verdict_data)

    @mock.patch("originality.ACCOUNTS_PATH", ACCOUNTS_PATH_TEST)
    def test_accounts_get_from_local(self):
        acc = self.test_account_data
        acc.name = ""
        acc.access_token = ""

        self.assertFalse(OriginalityAccount.get_from_local(21))
        self.assertEqual(OriginalityAccount.get_from_local(20), acc)

    def test_accounts_create(self):
        # TODO mock requests.Session
        pass

if __name__ == '__main__':
    unittest.main()
