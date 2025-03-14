import io
import csv
import json
import requests

def main():
    print(email.parse_email('example@gmail.com'))
    print(email.parse_email('example@gmail.gov.bs'))
    print(email.to_json('example@gmail.com'))
    print(email.to_json(['example@gmail.com']))
    print(email.to_json(['example@gmail.com', 'black.panther@hotmail.com']))
    print(url.parse_url('noaa.com/afwe?v=afwefn'))
    print(url.parse_url('noaa.com'))
    print(url.parse_url('noaa.com/afwe'))
    print(url.parse_url('www.noaa.com'))
    print(url.parse_url('www.noaa.com/directory'))
    print(url.parse_url('http://noaa.com/directory.txt'))
    print(url.parse_url('www.noaa.com/directory.txt'))
    print(url.parse_url('https://data.iana.org/TLD/tlds-alpha-by-domain.txt'))
    print(url.parse_url('https://www.bahamas.gov.bs/'))
    print(url.parse_url('https://guidance.data.gov.uk/publish_and_manage_data/'))
    print(url.to_json('https://guidance.data.gov.uk/publish_and_manage_data/'))
    print(url.to_json(['https://guidance.data.gov.uk/publish_and_manage_data/']))
    print(url.to_json(['https://guidance.data.gov.uk/publish_and_manage_data/', 'www.noaa.com/directory.txt']))

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

    def email_array(self, emails: list[str]) -> list[dict[str, dict[str, str]]] | None:
        """Parses each email in an array
        :param emails: list of emails
        :type emails: list[str]
        :return: parsed list of emails in a dictionary
        :rtype: list[dict[str, dict[str, str]]] | None
        """
        if not isinstance(emails, list) or len(emails) < 1:
            return None
        email_array = []
        for email in emails:
            email_array.append(self.parse_email(email))
        return email_array
    
    def to_json(self, emails: list[str] | str) -> list[dict[str, str]] | str | None:
        """Creates JSON string of emails
        :param emails: list of emails or singular email string
        :type emails: list[str] | str
        :return: list of dictionaries (or single dictionary) of emails in JSON format
        :rtype: list[dict[str, str]] | dict[str, str] | None
        """
        if isinstance(emails, str) or (isinstance(emails, list) and len(emails) == 1):
            email = [emails] if isinstance(emails, str) else emails
            result = self.parse_email(email[0])
            if result is None:
                return None
            return self.shared._to_json(result)
        if len(emails) >= 2:
            result = self.email_array(emails)
            if result is None:
                return None
            return self.shared._to_json(result)
        return

class Url:
    def __init__(self):
        self.shared = Shared()

    def parse_url(self, url_string:str, tlds: list[str] = []) -> dict[str, str] | None:
        """ Parses url addresses into component parts
        :param url_string: A string containing an email address
        :type url_string: str
        :param tlds: custom or up-to-date list of all current top level domains
        :type tlds: list[str]
        :return: dictionary containing url parsed into sub-parts
        :rtype: dict[str, str] | None
        """
        url_string = url_string.lower()
        url_dict = {'scheme': '', 'subdomain': '', 'second_level_domain': '', 
                    'top_level_domain': '', 'directories': ''}
        schemes = ['https', 'http']
        if not tlds:
            _, tlds = self.get_tld()
        scheme = url_string.split('://')[0]
        if not any(tld in url_string for tld in tlds) or (len([scheme]) >= 2 and scheme not in schemes):
            return None
        if scheme in schemes:
            url_dict['scheme'], url_string = url_string.split('://')

        temp = url_string.split('.')
        match len(temp):
            case 2:
                #example.org or example.org/directory
                tld_and_dir = temp[1].split('/')
                url_dict['top_level_domain'] = tld_and_dir[0] if tld_and_dir[0] in tlds else ''
                if not url_dict['top_level_domain']:
                    return None
                url_dict['second_level_domain'] = temp[0]
                url_dict['directories'] = "/".join(tld_and_dir[1:])
                return url_dict
            case 3:
                tld_and_dir = temp[2].split('/')
                if tld_and_dir[0] in tlds:
                    if temp[1] in tlds:
                        #example.gov.bs or example.gov.bs/directory
                        url_dict['second_level_domain'] = temp[0]
                        url_dict['top_level_domain'] = ".".join([temp[1], tld_and_dir[0]])
                        url_dict['directories'] = "/".join(tld_and_dir[1:])
                        return url_dict
                    #www.example.com or www.example.com/directory
                    url_dict['subdomain'] = temp[0]
                    url_dict['second_level_domain'] = temp[1]
                    url_dict['top_level_domain'] = tld_and_dir[0]
                    url_dict['directories'] = "/".join(tld_and_dir[1:])
                    return url_dict
                #example.org/directory.txt
                url_dict['second_level_domain'] = temp[0]
                temp = ".".join(temp[1:]).split('/')
                url_dict['top_level_domain'] = temp[0] if temp[0] in tlds else ''
                if not url_dict['top_level_domain']:
                    return None
                url_dict['directories'] = "/".join(temp[1:])
                return url_dict
            case 4:
                tld_and_dir = ".".join(temp[2:]).split('/')
                if all(tld in tlds for tld in tld_and_dir[0].split('.')):
                    #www.example.org/directory.xhtml or example.gov.bs/directory.xhtml
                    url_dict['subdomain'] = temp[0]
                    url_dict['second_level_domain'] = temp[1]
                    url_dict['top_level_domain'] = tld_and_dir[0]
                    url_dict['directories'] = "/".join(tld_and_dir[1:])
                    return url_dict
            case 5:
                tld_and_dir = ".".join(temp[3:]).split('/')
                if all(tld in tlds for tld in [temp[2], tld_and_dir[0]]):
                    #www.example.gov.bs/directory.xhtml
                    url_dict['subdomain'] = temp[0]
                    url_dict['second_level_domain'] = temp[1]
                    url_dict['top_level_domain'] = ".".join([temp[2], tld_and_dir[0]])
                    url_dict['directories'] = ".".join(tld_and_dir[1:])
                    return url_dict
        return None

    def url_array(self, urls: list[str], tlds: list[str] = []) -> list[str]:
        """Parses each url in an array
        :param urls: list of urls
        :type urls: list[str]
        :return: parsed list of urls in a dictionary
        :rtype: list[dict[str, dict[str, str]]] | None
        """
        url_list = []
        if not tlds:
            _, tlds = self.get_tld()
        for url in urls:
            url_list.append(self.parse_url(url, tlds))
        return url_list


    def to_json(self, urls: list[str] | str) -> list[dict[str, str]] | str | None:
        """Creates JSON string of urls
        :param urls: list of urls or singular url string
        :type urls: list[str] | str
        :return: list of dictionaries (or single dictionary) of urls in JSON format
        :rtype: list[dict[str, str]] | dict[str, str] | None
        """
        if isinstance(urls, str) or (isinstance(urls, list) and len(urls) == 1):
            url = [urls] if isinstance(urls, str) else urls
            result = self.parse_url(url[0])
            if result is None:
                return None
            return self.shared._to_json(result)
        if len(urls) >= 2:
            result = self.url_array(urls)
            if result is None:
                return None
            return self.shared._to_json(result)
        return None


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
    def _to_json(self, inputs: list[dict[str, dict[str, str]]] | dict[str, dict[str, str]] | dict[str, str] | list[str]) -> str:
        return json.dumps(inputs) #will write directly to json file eventually

    def _to_csv(self):
        pass

email = Email()
url = Url()

if __name__ == "__main__":
    main()
