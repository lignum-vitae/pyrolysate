import unittest
from pyrolysate import url

class TestUrl(unittest.TestCase):
    def test_parse_url_basic(self):
        """Test parsing of basic URL"""
        result = url.parse_url('example.com')
        self.assertEqual(result, 
        {'example.com':
            {
            'scheme': '',
            'subdomain': '',
            'second_level_domain': 'example',
            'top_level_domain': 'com',
            'directories': ''
            }
         })

    def test_parse_url_with_www(self):
        """Test parsing URL with www subdomain"""
        result = url.parse_url('www.example.com')
        self.assertEqual(result, 
        {'www.example.com':
            {
            'scheme': '',
            'subdomain': 'www',
            'second_level_domain': 'example',
            'top_level_domain': 'com',
            'directories': ''
            }
         })

    def test_parse_url_with_scheme(self):
        """Test parsing URL with http/https scheme"""
        result = url.parse_url('https://example.com')
        self.assertEqual(result, 
        {'https://example.com':
            {
            'scheme': 'https',
            'subdomain': '',
            'second_level_domain': 'example',
            'top_level_domain': 'com',
            'directories': ''
            }
         })

    def test_parse_url_with_directory(self):
        """Test parsing URL with directories"""
        result = url.parse_url('example.com/path/to/resource')
        self.assertEqual(result, 
        {'example.com/path/to/resource':
            {
            'scheme': '',
            'subdomain': '',
            'second_level_domain': 'example',
            'top_level_domain': 'com',
            'directories': 'path/to/resource'
            }
         })

    def test_parse_url_complex(self):
        """Test parsing complex URL with all components"""
        result = url.parse_url('https://www.example.com/path/to/resource.html')
        self.assertEqual(result, 
        {'https://www.example.com/path/to/resource.html':
            {
            'scheme': 'https',
            'subdomain': 'www',
            'second_level_domain': 'example',
            'top_level_domain': 'com',
            'directories': 'path/to/resource.html'
            }
         })

    def test_parse_url_government_domain(self):
        """Test parsing government domain URLs"""
        result = url.parse_url('https://data.gov.uk/dataset')
        self.assertEqual(result, 
        {'https://data.gov.uk/dataset':
            {
            'scheme': 'https',
            'subdomain': '',
            'second_level_domain': 'data',
            'top_level_domain': 'gov.uk',
            'directories': 'dataset'
            }
         })

    def test_parse_url_invalid_scheme(self):
        """Test parsing URL with invalid scheme"""
        schemes = ['ftp', 'htp', 'nes', 'message']
        for scheme in schemes:
            result = url.parse_url(f'{scheme}://example.com')
            self.assertIsNone(result)

    def test_parse_empty_url_string(self):
        """Test parsing URL with invalid scheme"""
        urls = [[''], [], '']
        for x in urls:
            result = url.parse_url(x)
            self.assertIsNone(result)

    def test_parse_empty_url_array(self):
        """Test parsing URL with invalid scheme"""
        urls = [[''], [], '']
        for x in urls:
            result = url.parse_url_array(x)
            self.assertIsNone(result)

    def test_parse_url_invalid_tld(self):
        """Test parsing URL with invalid top-level domain"""
        result = url.parse_url('example.invalidtld')
        self.assertIsNone(result)

    def test_url_array_valid(self):
        """Test parsing array of valid URLs"""
        urls = ['example.com', 'www.test.org']
        result = url.parse_url_array(urls)
        self.assertEqual(result, 
        {'example.com':
            {
                'scheme': '',
                'subdomain': '',
                'second_level_domain': 'example',
                'top_level_domain': 'com',
                'directories': ''
            }, 
         'www.test.org':
            {
                'scheme': '',
                'subdomain': 'www',
                'second_level_domain': 'test',
                'top_level_domain': 'org',
                'directories': ''
            }
         })

    def test_to_json_single_url(self):
        """Test JSON conversion of single URL"""
        result = url.to_json('example.com')
        self.assertIsInstance(result, str)
        self.assertIn('second_level_domain', result)
        self.assertIn('top_level_domain', result)

    def test_to_json_multiple_urls(self):
        """Test JSON conversion of multiple URLs"""
        urls = ['example.com', 'test.org']
        result = url.to_json(urls)
        self.assertIsInstance(result, str)
        self.assertIn('"second_level_domain": "example", "top_level_domain": "com"', result)
        self.assertIn('"second_level_domain": "test", "top_level_domain": "org"', result)

    def test_to_json_invalid_url(self):
        """Test JSON conversion of invalid URL"""
        result = url.to_json('invalid.invalidtld')
        self.assertIsNone(result)

    def test_to_json_empty(self):
        """Test JSON conversion of empty list"""
        result = url.to_json([])
        self.assertIsNone(result)

        result = url.to_json('')
        self.assertIsNone(result)

    def test_parse_url_with_custom_tlds(self):
        """Test parsing URL with custom TLD list"""
        custom_tlds = ['com', 'net', 'custom']
        result = url.parse_url('example.custom', tlds=custom_tlds)
        self.assertEqual(result, {'example.custom':
        {
            'scheme': '',
            'subdomain': '',
            'second_level_domain': 'example',
            'top_level_domain': 'custom',
            'directories': ''
        }})

    def test_get_tld(self):
        """Test fetching TLDs from IANA"""
        last_updated, tlds = url.get_tld()
        self.assertIsInstance(last_updated, str)
        self.assertIsInstance(tlds, list)
        self.assertGreater(len(tlds), 0)
        # Check for some common TLDs
        self.assertIn('com', tlds)
        self.assertIn('org', tlds)
        self.assertIn('net', tlds)
        self.assertIn('io', tlds)

    def test_to_csv_single_url(self):
        """Test CSV conversion of single URL"""
        result = url.to_csv('example.com')
        self.assertIsInstance(result, str)
        self.assertIn('second_level_domain', result)
        self.assertIn('top_level_domain', result)

    def test_to_csv_multiple_urls(self):
        """Test CSV conversion of multiple URLs"""
        urls = ['example.com', 'test.org']
        result = url.to_csv(urls)
        self.assertIsInstance(result, str)
        self.assertIn('example.com', result)
        self.assertIn('example', result)
        self.assertIn('com', result)
        self.assertIn('test.org', result)
        self.assertIn('test', result)
        self.assertIn('org', result)

    def test_to_csv_invalid_url(self):
        """Test CSV conversion of invalid URL"""
        result = url.to_csv('invalid.invalidtld')
        self.assertIsNone(result)

    def test_to_csv_empty(self):
        """Test CSV conversion of empty list"""
        result = url.to_csv([])
        self.assertIsNone(result)

        result = url.to_csv('')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
