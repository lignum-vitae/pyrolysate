# Pyrolysate

A Python library for parsing URLs and email addresses into structured JSON and CSV formats. 
The library handles various URL formats and email patterns, providing consistent output structures.

## 🚀 Installation
### 1. Clone the Repository
First, clone the repository to your local machine using Git:

```bash
git clone https://github.com/lignum-vitae/pyrolysate
cd pyrolysate/pyrolysate
python converter.py
```
### 2. Pip install (not yet available)
```bash
pip install pyrolysate
```
## Testing
To run all tests from command line, run one of the following commands from the project's root directory
```bash
py -m unittest discover tests
python -m unittest discover tests
python3 -m unittest discover tests
```

## Features

- Parse URLs and email addresses into structured data
- Support for complex URL patterns including ports, queries, and fragments
- Support for government domain emails (.gov.tld)
- Export to JSON and CSV formats
- Fetch up-to-date TLD list from IANA
- Support for IP addresses in URLs
- Uses Python's built-in generators to handle large lists of URLs or email addresses without excessive memory consumption

## Usage

### Email Parsing

```python
from pyrolysate import email
```
#### Parse single email
```python
result = email.parse_email("user@example.com")
```
#### Parse multiple emails
```python
emails = ["user1@example.com", "user2@agency.gov.uk"]
result = email.parse_email_array(emails)
```
#### Convert to JSON
```python
json_output = email.to_json("user@example.com")
json_output = email.to_json(["user1@example.com", "user2@example.com"])
```
#### Export to CSV
```python
csv_output = email.to_csv("user@example.com")
email.to_csv_file("output", ["user1@example.com", "user2@example.com"])
```

### URL Parsing

```python
from pyrolysate import url
```

#### Parse single URL
```python
result = url.parse_url("https://www.example.com/path?q=test#fragment")
```
#### Parse multiple URLs
```python
urls = ["example.com", "https://www.test.org"]
result = url.parse_url_array(urls)
```
#### Convert to JSON
```python
json_output = url.to_json("example.com")
json_output = url.to_json(["example.com", "test.org"])
```
#### Export to CSV
```python
csv_output = url.to_csv("example.com")
url.to_csv_file("output", ["example.com", "test.org"])
```
## API Reference

### Email Class

| Method                                           | Parameters                                              | Description                    |
|---------------------                             |---------------------                                    |-----------------               |
| `parse_email(email_str)`                         | `email_str: str`                                        | Parses single email address    |
| `parse_email_array(emails)`                      | `emails: list[str]`                                     | Parses list of email addresses |
| `to_json(emails, prettify=True)`                 | `emails: str\|list[str]`, `prettify: bool`              | Converts to JSON format        |
| `to_json_file(file_name, emails, prettify=True)` | `file_name: str`, `emails: list[str]`, `prettify: bool` | Converts and saves JSON to file|
| `to_csv(emails)`                                 | `emails: str\|list[str]`                                | Converts to CSV format         |
| `to_csv_file(file_name, emails)`                 | `file_name: str`, `emails: list[str]`                   | Converts and saves CSV to file |

### URL Class

| Method                                         | Parameters                                            | Description                        |
|------------------                              |----------------------                                 |-------------------                 |
| `parse_url(url_str, tlds=[])`                  | `url_str: str`, `tlds: list[str]`                     | Parses single URL                  |
| `parse_url_array(urls, tlds=[])`               | `urls: list[str]`, `tlds: list[str]`                  | Parses list of URLs                |
| `to_json(urls, prettify=True)`                 | `urls: str\|list[str]`, `prettify: bool`              | Converts to JSON format            |
| `to_json_file(file_name, urls, prettify=True)` | `file_name: str`, `urls: list[str]`, `prettify: bool` | Converts and saves JSON to file    |
| `to_csv(urls)`                                 | `urls: str\|list[str]`                                | Converts to CSV format             |
| `to_csv_file(file_name, urls)`                 | `file_name: str`, `urls: list[str]`                   | Converts and saves CSV to file     |
| `get_tld()`                                    | None                                                  | Fetches current TLD list from IANA |

## Output Formats

### Email Parse Output

| Field       | Description       | Example |
|-------------|-------------------|---------|
| username    | Part before @     | user    |
| mail_server | Domain before TLD | gmail   |
| domain      | Top-level domain  | com     |

Example output:
```json
{"user@gmail.com": 
    {
    "username": "user",
    "mail_server": "gmail",
    "domain": "com"
    }
}
```

```csv
email,username,mail_server,domain
user@gmail.com,user,gmail,com
```


### URL Parse Output

| Field               | Description      | Example   |
|--------------       |---------------   |---------  |
| scheme              | Protocol         | https     |
| subdomain           | Domain prefix    | www       |
| second_level_domain | Main domain      | example   |
| top_level_domain    | Domain suffix    | com       |
| port                | Port number      | 443       |
| path                | URL path         | blog/post |
| query               | Query parameters | q=test    |
| fragment            | URL fragment     | section1  |

Example output:
```json
{"https://www.example.com:443/blog/post?q=test#section1": 
    {
    "scheme": "https",
    "subdomain": "www",
    "second_level_domain": "example",
    "top_level_domain": "com",
    "port": "443",
    "path": "blog/post",
    "query": "q=test",
    "fragment": "section1"
    }
}
```

```csv
url,scheme,subdomain,second_level_domain,top_level_domain,port,path,query,fragment
https://www.example.com:443/blog/post?q=test#section1,https,www,example,com,443,blog/post,q=test,section1
```

## Supported Formats

### Email Formats
- Standard: `example@mail.com`
- Government: `example@agency.gov.uk`

### URL Formats
- Basic: `example.com`
- With subdomain: `www.example.com`
- With scheme: `https://example.com`
- With path: `example.com/path/to/file.txt`
- With port: `example.com:8080`
- With query: `example.com/search?q=test`
- With fragment: `example.com#section1`
- IP addresses: `192.168.1.1:8080`
- Government domains: `agency.gov.uk`
- Full complex URLs: `https://www.example.gov.uk:8080/path?q=test#section1`
