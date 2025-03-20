from io import StringIO
import csv
import json
import requests

def main():
    print(url.to_json('www.example.gov.bs/directory.xhtml'))
    print(url.to_json('example.gov.bs'))
    print(url.to_json('example.gov.bs/directory'))
    print(url.to_json('www.example.com'))
    print(url.to_json('https://www.example.com/directory'))
    print(url.to_json('http://example.org/sub/cc/directory.txt'))
    print(url.to_json('https://www.example.gov.bs/sub/cc/directory?docid=720&hl=en#dayone'))
    print(url.to_json('https://www.example.gov.bs:7105/sub/cc/directory?docid=720&hl=en#dayone'))
    print(url.to_json('https://www.example.gov.bs:7102'))
    print(url.to_json('https://93.184.216.34:7102'))
    print(url.to_json('https://93.184.216.34:7105/sub/cc/directory?docid=720&hl=en#dayone'))
    print(url.to_json('example.com/path/?#'))
    print(url.to_json('example.com/path/#'))
    print(url.to_json('example.com/path/?'))

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
    
    def to_json(self, emails: list[str] | str, prettify=True) -> list[dict[str, str]] | str | None:
        """Creates JSON string of emails
        :param emails: list of emails or singular email string
        :type emails: list[str] | str
        :return: list of dictionaries (or single dictionary) of emails in JSON format
        :rtype: list[dict[str, str]] | dict[str, str] | None
        """
        return self.shared._to_json(self.parse_email, self.parse_email_array, emails, prettify)

    def to_json_file(self, file_name: str, emails: list[str], prettify: bool=True) -> str:
        success = self.shared._to_json_file(self.parse_email, self.parse_email_array, file_name, emails, prettify)
        if not success:
            return "Failed to write file"
        return "File successfully written"

    def to_csv(self, emails: list[str] | str) -> str | None:
        header = ['email', 'username', 'mail_server', 'domain']
        field_generator = lambda entry, details: [
                entry, 
                details['username'], 
                details['mail_server'], 
                details['domain'] 
                ]
        return self.shared._to_csv(header, field_generator, self.parse_email, self.parse_email_array, emails)

    def to_csv_file(self, file_name, urls: list[str] | str) -> str:
        header = ['email', 'username', 'mail_server', 'domain']
        field_generator = lambda entry, details: [
                entry, 
                details['username'], 
                details['mail_server'], 
                details['domain'] 
                ]
        success = self.shared._to_csv_file(header, field_generator, self.parse_email, self.parse_email_array, file_name, urls)
        if not success:
            return "Failed to write file"
        return "File successfully written"

class Url:
    def __init__(self):
        self.shared = Shared()
        self.header = ["url", "scheme", "subdomain", "second_level_domain", 
                       "top_level_domain","port", "path", "query", "fragment"]
        self.field_generator = lambda entry, details: [
                entry, 
                details['scheme'], 
                details['subdomain'], 
                details['second_level_domain'], 
                details['top_level_domain'], 
                details['port'],
                details['path'],
                details['query'],
                details['fragment']
                ]

    def parse_url(self, url_string:str, tlds: list[str] = []) -> dict[str, dict[str, str]] | None:
        """ Parses url addresses into component parts
        :param url_string: A string containing an email address
        :type url_string: str
        :param tlds: custom or up-to-date list of all current top level domains
        :type tlds: list[str]
        :return: dictionary containing url parsed into sub-parts
        :rtype: dict[str, str] | None
        """
        if not isinstance(url_string, str) or len(url_string) == 0:
            return None
        ip_present = False
        url_string = url_string.lower()
        temp_url_string = url_string
        
        url_dict = {url_string: {'scheme': '', 'subdomain': '', 'second_level_domain': '', 
                                 'top_level_domain': '', 'port': '', 'path': '', 
                                 'query': '', 'fragment': ''}}
        schemes = ['https', 'http']
        default_ports = {'https':"443", 'http':"80"}
        if not tlds:
            _, tlds = self.get_tld()
        scheme = url_string.split('://')[0]
        if '://' in url_string and scheme not in schemes:
            return None
        if scheme in schemes:
            url_dict[url_string]['scheme'], temp_url_string = url_string.split('://')
            url_dict[url_string]['port'] = default_ports[url_dict[url_string]['scheme']]
            

        if ":" in temp_url_string:
            domain_port_etc = temp_url_string.split(":")
            port_etc = domain_port_etc[1].split("/")
            url_dict[url_string]['port'] = port_etc[0]
            port_etc.append("")
            temp_url_string = domain_port_etc[0]+"/"+"/".join(port_etc[1:])

        parts = temp_url_string.split("/")
        parts = parts[0].split(".")
        if all(part.isdigit() and 0 <= int(part) <= 255 for part in parts[:4]):
            ip_present = True
            url_dict[url_string]['top_level_domain'] = ".".join(parts[:4])

        if ip_present is False and not any(tld in url_string for tld in tlds):
            url_dict[url_string]['scheme'] = ""
            url_dict[url_string]['port'] = ""
            return url_dict

        temp = temp_url_string.split('.')
        temp_len = len(temp)
        match temp_len:
            case 2:
                #example.org or example.org/directory
                tld_and_dir = temp[1].split('/')
                if tld_and_dir[0] in tlds:
                    url_dict[url_string]['second_level_domain'] = temp[0]
                    url_dict[url_string]['top_level_domain'] = tld_and_dir[0]
            case 3:
                tld_and_dir = temp[2].split('/')
                if tld_and_dir[0] in tlds:
                    if temp[1] in tlds:
                        #example.gov.bs or example.gov.bs/directory
                        url_dict[url_string]['second_level_domain'] = temp[0]
                        url_dict[url_string]['top_level_domain'] = ".".join([temp[1], tld_and_dir[0]])
                    else:
                        #www.example.com or www.example.com/directory
                        url_dict[url_string]['subdomain'] = temp[0]
                        url_dict[url_string]['second_level_domain'] = temp[1]
                        url_dict[url_string]['top_level_domain'] = tld_and_dir[0]
                else:
                    #example.org/directory.txt
                    if temp[1].split("/")[0] in tlds:
                        url_dict[url_string]['second_level_domain'] = temp[0]
                        temp = ".".join(temp[1:]).split('/')
                        url_dict[url_string]['top_level_domain'] = temp[0]
                        tld_and_dir = temp[:]
            case 4:
                tld_and_dir = ".".join(temp[2:]).split('/')
                if all(tld in tlds for tld in tld_and_dir[0].split('.')):
                    #www.example.org/directory.xhtml or example.gov.bs/directory.xhtml
                    url_dict[url_string]['subdomain'] = temp[0]
                    url_dict[url_string]['second_level_domain'] = temp[1]
                    url_dict[url_string]['top_level_domain'] = tld_and_dir[0]
            case 5:
                tld_and_dir = ".".join(temp[3:]).split('/')
                if all(tld in tlds for tld in [temp[2], tld_and_dir[0]]):
                    #www.example.gov.bs/directory.xhtml
                    url_dict[url_string]['subdomain'] = temp[0]
                    url_dict[url_string]['second_level_domain'] = temp[1]
                    url_dict[url_string]['top_level_domain'] = ".".join([temp[2], tld_and_dir[0]])
            case _:
                url_dict[url_string]['scheme'] = ""
                return url_dict

        if url_dict[url_string]['top_level_domain'] == "":
            url_dict[url_string]['scheme'] = ""
            url_dict[url_string]['port'] = ""
            return url_dict

        path_query_fragment =  "/".join(tld_and_dir[1:])
        if "?" not in path_query_fragment and "#" not in path_query_fragment:
            path = path_query_fragment.strip("/")
            url_dict[url_string]['path'] = path

        elif "?" in path_query_fragment:
            path_query = [value.strip("/") for value in path_query_fragment.split("?")]
            url_dict[url_string]['path'] = path_query[0]
            if "#" in path_query[1]:
                fragment = path_query[1].split("#")
                url_dict[url_string]['query'] = fragment[0]
                if len(fragment) >= 2:
                    url_dict[url_string]['fragment'] = "".join(fragment[1:])
            elif len(path_query) >= 2:
                url_dict[url_string]['query'] = "".join(path_query[1:])
        elif "#" in path_query_fragment:
            fragment = [value.strip("/") for value in path_query_fragment.split("#")]
            url_dict[url_string]['path'] = fragment[0]
            if len(fragment) >= 2:
                url_dict[url_string]['fragment'] = "".join(fragment[1:])
        
        return url_dict

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

    def to_json(self, urls: list[str] | str, prettify=True) -> list[dict[str, str]] | str | None:
        """Creates JSON string of urls
        :param urls: list of urls or singular url string
        :type urls: list[str] | str
        :return: list of dictionaries (or single dictionary) of urls in JSON format
        :rtype: list[dict[str, str]] | dict[str, str] | None
        """
        return self.shared._to_json(self.parse_url, self.parse_url_array, urls, prettify)

    def to_json_file(self, file_name: str, urls: list[str], prettify: bool=True) -> str:
        success = self.shared._to_json_file(self.parse_url, self.parse_url_array, file_name, urls, prettify)
        if not success:
            return "Failed to write file"
        return "File successfully written"

    def to_csv(self, urls: list[str] | str) -> str | None:
        return self.shared._to_csv(self.header, self.field_generator, self.parse_url, self.parse_url_array, urls)

    def to_csv_file(self, file_name, urls: list[str] | str) -> str:
        success = self.shared._to_csv_file(self.header, self.field_generator, self.parse_url, self.parse_url_array, file_name, urls)
        if not success:
            return "Failed to write file"
        return "File successfully written"

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
    def _validate_data(self, string_parse, array_parse, data) -> dict[str, dict[str, str]] | None:
        results = None
        if not isinstance(data, str) and not isinstance(data, list):
            return None
        if isinstance(data, str) or (isinstance(data, list) and len(data) == 1):
            data = [data] if isinstance(data, str) else data
            results = string_parse(data[0])
        if len(data) >= 2:
            results = array_parse(data)
        if results is not None:
            return results
        return None

    def _to_json(self, string_parse, array_parse, data, pretty) -> str | None:
        result = self._validate_data(string_parse, array_parse, data)
        if result is None:
            return None
        if not pretty:
            return json.dumps(result)
        return json.dumps(result, indent=4)

    def _to_json_file(self, string_parse, array_parse, file_name, data, pretty) -> bool:
        result = self._validate_data(string_parse, array_parse, data)
        if result is None:
            return False
        if not pretty:
            with open(f"{file_name}.json", 'w') as file:
                json.dump(result, file)
        if pretty:    
            with open(f"{file_name}.json", 'w') as file:
                json.dump(result, file, indent=4)
        return True

    def _to_csv(self, headers, data_fields, string_parse, array_parse, data) -> str | None:
        result = self._validate_data(string_parse, array_parse, data)
        if result is None:
            return None
        buffer = StringIO() #Open StringIO object
        csv_writer = csv.writer(buffer)
        csv_writer.writerow(headers)
        for entry, details in result.items():
            csv_writer.writerow(data_fields(entry, details))
        csv_data = buffer.getvalue()
        buffer.close() #Close the StringIO object
        return csv_data

    def _to_csv_file(self, headers, data_fields, string_parse, array_parse, file_name, data) -> bool:
        result = self._validate_data(string_parse, array_parse, data)
        if result is None:
            return False
        with open(f"{file_name}.csv", 'w') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(headers)
            for entry, details in result.items():
                csv_writer.writerow(data_fields(entry, details))
        return True

email = Email()
url = Url()

if __name__ == "__main__":
    main()
