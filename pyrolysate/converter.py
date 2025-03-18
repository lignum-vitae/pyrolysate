from io import StringIO
import csv
import json
import requests

def main():
    print(email.parse_email('example@gmail.com'))
    print(email.parse_email_array(['example@gmail.com',
                                   'example@treasury.gov.bs']))
    print(url.parse_url('https://www.ryugod.com/pages/ide/python'))
    print(url.parse_url_array(['https://www.ryugod.com/pages/ide/python',
                               'https://www.youtube.com/watch?v=W1htfqXyX6M&ab_channel=PhilipDeFranco']))

class Email:
    def __init__(self):
        self.shared = Shared()

    def parse_email(self, e_mail_string: str) -> dict[str, dict[str, str]] | None:
        """ Parses email addresses into component parts
        :param e_mail_string: A string containing an email address
        :type e_mail_string: str
        :return: Dictionary containing email parsed into sub-parts
        :rtype: dict[str, str] | None
        """
        email_dict = {e_mail_string: {"username": "", "mail_server": "", "domain": "", }}
        temp = e_mail_string.split('@')
        if len(temp) != 2: 
            return None #returns none for invalid emails without @
        email_dict[e_mail_string]["username"] = temp[0]
        server_and_domain = temp[1].split('.')
        if len(server_and_domain) > 3:
            return None #invalid email with too many periods
        email_dict[e_mail_string]["mail_server"] = server_and_domain[0]
        #handles emails ending in standard tld or government emails (.gov.bs)
        email_dict[e_mail_string]["domain"] = ".".join(server_and_domain[1:])
        return email_dict

    def parse_email_array(self, emails: list[str]) -> dict[str, dict[str, str]] | None:
        """Parses each email in an array
        :param emails: list of emails
        :type emails: list[str]
        :return: parsed list of emails in a dictionary
        :rtype: list[dict[str, dict[str, str]]] | None
        """
        if not isinstance(emails, list) or len(emails) < 1:
            return None
        email_dict = {}
        for email in emails:
            if email not in email_dict:
                email_dict.update(self.parse_email(email))
        return email_dict
    
    def to_json(self, emails: list[str] | str) -> list[dict[str, str]] | str | None:
        """Creates JSON string of emails
        :param emails: list of emails or singular email string
        :type emails: list[str] | str
        :return: list of dictionaries (or single dictionary) of emails in JSON format
        :rtype: list[dict[str, str]] | dict[str, str] | None
        """
        return self.shared._to_json(self.parse_email, self.parse_email_array, emails)

class Url:
    def __init__(self):
        self.shared = Shared()

    def parse_url(self, url_string:str, tlds: list[str] = []) -> dict[str, dict[str, str]] | None:
        """ Parses url addresses into component parts
        :param url_string: A string containing an email address
        :type url_string: str
        :param tlds: custom or up-to-date list of all current top level domains
        :type tlds: list[str]
        :return: dictionary containing url parsed into sub-parts
        :rtype: dict[str, str] | None
        """
        if not isinstance(url_string, str) or not url_string:
            return None
        url_string = url_string.lower()
        temp_url_string = url_string
        
        url_dict = {url_string: {'scheme': '', 'subdomain': '', 'second_level_domain': '', 
                    'top_level_domain': '', 'directories': ''}}
        schemes = ['https', 'http']
        if not tlds:
            _, tlds = self.get_tld()
        scheme = url_string.split('://')[0]
        if not any(tld in url_string for tld in tlds) or (len([scheme]) >= 2 and scheme not in schemes):
            return None
        if '://' in url_string and scheme not in schemes:
            return None
        if scheme in schemes:
            url_dict[url_string]['scheme'], temp_url_string = url_string.split('://')

        temp = temp_url_string.split('.')
        match len(temp):
            case 2:
                #example.org or example.org/directory
                tld_and_dir = temp[1].split('/')
                url_dict[url_string]['top_level_domain'] = tld_and_dir[0] if tld_and_dir[0] in tlds else ''
                if not url_dict[url_string]['top_level_domain']:
                    return None
                url_dict[url_string]['second_level_domain'] = temp[0]
                url_dict[url_string]['directories'] = "/".join(tld_and_dir[1:])
                return url_dict
            case 3:
                tld_and_dir = temp[2].split('/')
                if tld_and_dir[0] in tlds:
                    if temp[1] in tlds:
                        #example.gov.bs or example.gov.bs/directory
                        url_dict[url_string]['second_level_domain'] = temp[0]
                        url_dict[url_string]['top_level_domain'] = ".".join([temp[1], tld_and_dir[0]])
                        url_dict[url_string]['directories'] = "/".join(tld_and_dir[1:])
                        return url_dict
                    #www.example.com or www.example.com/directory
                    url_dict[url_string]['subdomain'] = temp[0]
                    url_dict[url_string]['second_level_domain'] = temp[1]
                    url_dict[url_string]['top_level_domain'] = tld_and_dir[0]
                    url_dict[url_string]['directories'] = "/".join(tld_and_dir[1:])
                    return url_dict
                #example.org/directory.txt
                url_dict[url_string]['second_level_domain'] = temp[0]
                temp = ".".join(temp[1:]).split('/')
                url_dict[url_string]['top_level_domain'] = temp[0] if temp[0] in tlds else ''
                if not url_dict[url_string]['top_level_domain']:
                    return None
                url_dict[url_string]['directories'] = "/".join(temp[1:])
                return url_dict
            case 4:
                tld_and_dir = ".".join(temp[2:]).split('/')
                if all(tld in tlds for tld in tld_and_dir[0].split('.')):
                    #www.example.org/directory.xhtml or example.gov.bs/directory.xhtml
                    url_dict[url_string]['subdomain'] = temp[0]
                    url_dict[url_string]['second_level_domain'] = temp[1]
                    url_dict[url_string]['top_level_domain'] = tld_and_dir[0]
                    url_dict[url_string]['directories'] = "/".join(tld_and_dir[1:])
                    return url_dict
            case 5:
                tld_and_dir = ".".join(temp[3:]).split('/')
                if all(tld in tlds for tld in [temp[2], tld_and_dir[0]]):
                    #www.example.gov.bs/directory.xhtml
                    url_dict[url_string]['subdomain'] = temp[0]
                    url_dict[url_string]['second_level_domain'] = temp[1]
                    url_dict[url_string]['top_level_domain'] = ".".join([temp[2], tld_and_dir[0]])
                    url_dict[url_string]['directories'] = ".".join(tld_and_dir[1:])
                    return url_dict
        return None

    def parse_url_array(self, urls: list[str], tlds: list[str] = []) -> dict[str, str] | None:
        """Parses each url in an array
        :param urls: list of urls
        :type urls: list[str]
        :return: parsed list of urls in a dictionary
        :rtype: list[dict[str, dict[str, str]]] | None
        """
        if not urls or all(item == "" for item in urls) or not isinstance(urls, list):
            return None
        url_dict = {}
        if not tlds:
            _, tlds = self.get_tld()
        for url in urls:
            if url not in url_dict:
                url_dict.update(self.parse_url(url, tlds))
        return url_dict

    def to_json(self, urls: list[str] | str) -> list[dict[str, str]] | str | None:
        """Creates JSON string of urls
        :param urls: list of urls or singular url string
        :type urls: list[str] | str
        :return: list of dictionaries (or single dictionary) of urls in JSON format
        :rtype: list[dict[str, str]] | dict[str, str] | None
        """
        return self.shared._to_json(self.parse_url, self.parse_url_array, urls)

    def get_tld(self) -> tuple[str, list[str]]:
        """ Grabs top level domains from internet assigned numbers authority
        :return: List of up-to-date top level domains and date list was last updated
        :rtype: tuple[str, list[str]]
        """
        response = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt')
        lines = response.text.split('\n')
        last_updated = lines[0]
        tlds = list(map(lambda x: x.lower(), filter(None, lines[1:]))) #removes empty strings from list of top level domains
        return last_updated, tlds

class Shared:
    def _to_json(self, string_parse, array_parse, data) -> str | None:
        if isinstance(data, str) or (isinstance(data, list) and len(data) == 1):
            data = [data] if isinstance(data, str) else data
            result = string_parse(data[0])
            if result is None:
                return None
            return json.dumps(result)
        if len(data) >= 2:
            result = array_parse(data)
            if result is None:
                return None
            return json.dumps(result)
        return None

    def _to_json_file(self):
        raise NotImplementedError()

    def _to_csv(self, header, data_type, data) -> str:
        raise NotImplementedError()

    def _to_csv_file(self):
        raise NotImplementedError()

email = Email()
url = Url()

if __name__ == "__main__":
    main()
