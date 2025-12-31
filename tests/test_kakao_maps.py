import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
from src.kakao_map_api import get_coordinates

class KakaoMapApiTest(unittest.TestCase):

    @patch('requests.get')
    def test_get_coordinates(self, mock_get):
        # Mock response from the Kakao Maps API
        mock_response = {
            'documents': [
                {
                    'y': '37.5665',
                    'x': '126.9780'
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        # Call the function with a test address
        lat, lon = get_coordinates('서울시청')

        # Assert that the function returns the correct coordinates
        self.assertEqual(lat, 37.5665)
        self.assertEqual(lon, 126.9780)

if __name__ == '__main__':
    unittest.main()