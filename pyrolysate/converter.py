# required installs
import requests

# built-ins
import csv
import json
from io import StringIO
from datetime import datetime

# function decorators for memoization
from functools import cache

# Generator type hints and type checking
from typing import Generator
import collections.abc

def main():
    print(email.parse_email("user+facebook@gmail.com"))
    print(email.to_csv("user+facebook@gmail.com"))
    print(email.to_csv(["user+facebook@gmail.com", "football@hotmail.com", "happy+yoohoo@messenger.org"]))

    print(url.to_csv("www.youtube.com"))
    print(url.to_csv("www.youtube.com/directory.xhtml"))

def parse_input_file(input_file_name: str, delimiter: str = '\n') -> list[str] | None:
    if not isinstance(input_file_name, str):
        return None
    try:
        with open(input_file_name, 'r') as file:
            result = file.read()
    except OSError as err:
        print("OS error:", err)
        return None
    except IOError as err:
        print("An error occured while attempting to read the file.")
        return None
    except PermissionError as err:
        print("You do not have permission to open file.")
        return None
    except FileNotFoundError as err:
        print("Unable to locate file.")
        return None

    temp = [x.strip() for x in result.split(delimiter) if x != '']
    return temp

class Email:
    def __init__(self):
        self.shared = Shared()
        self.header = ['email', 'username', 'plus_address', 'mail_server', 'domain']
        self.empty_dict = {field: "" for field in self.header[1:]}
        self.field_generator = lambda entry, details: [entry] + [details[field] for field in self.header[1:]]

    def parse_email(self, e_mail_string: str) -> dict[str, dict[str, str]] | None:
        """ Parses email addresses into component parts
        :param e_mail_string: A string containing an email address
        :type e_mail_string: str
        :return: Dictionary containing email parsed into sub-parts
        :rtype: dict[str, dict[str, str]] | None
        """
        if not isinstance(e_mail_string, str) or len(e_mail_string) == 0:
            return None
        email_dict = {e_mail_string: self.empty_dict.copy()}
        temp = e_mail_string.split('@')
        if len(temp) != 2:
            return None #returns none for invalid emails without @ or multiple @
        plus_address = temp[0].split('+')
        if len(plus_address) == 2:
            email_dict[e_mail_string]["username"] = plus_address[0]
            email_dict[e_mail_string]["plus_address"] = plus_address[1]
        else:
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
        :rtype: dict[str, dict[str, str]] | None
        """
        results = self._parse_email_array(emails)
        if results == None:
            return None

        email_array = {}
        for result in results:
            if result == None:
                continue
            email_array.update(result)

        if email_array == {}:
            return None
        return email_array

    def _parse_email_array(self, emails: list[str]) -> Generator[dict[str, dict[str, str]], None, None] | None:
        """Parses each email in an array
        :param emails: list of emails
        :type emails: list[str]
        :return: parsed list of emails in a dictionary
        :rtype: dict[str, dict[str, str]] | None
        """
        if not isinstance(emails, list) or len(emails) < 1:
            return None
        for email in emails:
            yield self.parse_email(email)

    def to_json(self, emails: list[str] | str, prettify=True) -> str | None:
        """Creates a JSON string representation of emails.
        :param emails: A list of emails or a single email string.
        :type emails: list[str] | str
        :param prettify: Whether to format the JSON output with indentation for readability.
        :type prettify: bool, optional (default is True)
        :return: A JSON string of the parsed emails or None if the input is invalid or empty.
        :rtype: str | None
        """
        return self.shared._to_json(self.parse_email, self._parse_email_array, emails, prettify)

    def to_json_file(self, file_name: str, emails: list[str], prettify: bool=True) -> tuple[str, int]:
        """Writes parsed emails to a JSON file.
        :param file_name: The name of the file (without extension) to write the JSON data.
        :type file_name: str
        :param emails: A list of emails to parse and write to the file.
        :type emails: list[str]
        :param prettify: Whether to format the JSON output with indentation for readability.
        :type prettify: bool, optional (default is True)
        :return: A tuple containing the file name with extension and an int. 0 for a pass, 1 for a fail.
        :rtype: tuple[str, int]
        """
        return self.shared._to_json_file(self.parse_email, self._parse_email_array, file_name, emails, prettify)

    def to_csv(self, emails: list[str] | str) -> str | None:
        """Creates a CSV string representation of URLs.
        :param urls: A list of URLs or a single URL string.
        :type urls: list[str] | str
        :return: A CSV string of the parsed URLs or None if the input is invalid or empty.
        :rtype: str | None
        """
        return self.shared._to_csv(self.header, self.field_generator, self.parse_email, self._parse_email_array, emails)

    def to_csv_file(self, file_name, urls: list[str] | str) -> tuple[str, int]:
        """Writes parsed emails to a CSV file.
        :param file_name: The name of the file (without extension) to write the CSV data.
        :type file_name: str
        :param emails: A list of emails or a single email string to parse and write to the file.
        :type emails: list[str] | str
        :return: A tuple containing the file name with extension and an int. 0 for a pass, 1 for a fail.
        :rtype: tuple[str, int]
        """
        return self.shared._to_csv_file(self.header, self.field_generator, self.parse_email, self._parse_email_array, file_name, urls)

class Url:
    def __init__(self):
        self.shared = Shared()
        self.schemes_and_ports = {"https":"443", "http":"80"}
        self.two_part_tlds_lhs = ['gov', 'co', 'com', 'org', 'net', 'ac', 'edu', 'net', 'or', 'ne', 'go']
        self.header = ["url", "scheme", "subdomain", "second_level_domain",
                       "top_level_domain","port", "path", "query", "fragment"]
        self.empty_dict = {field: "" for field in self.header[1:]}
        self.field_generator = lambda entry, details: [entry] + [details[field] for field in self.header[1:]]

    def parse_url(self, url_string:str, tlds: list[str] | None = None) -> dict[str, dict[str, str]] | None:
        """ Parses url addresses into component parts
        :param url_string: A string containing a url
        :type url_string: str
        :param tlds: custom or up-to-date list of all current top level domains
        :type tlds: list[str]
        :return: dictionary containing url parsed into sub-parts
        :rtype: dict[str, dict[str, str]] | None
        """
        if not isinstance(url_string, str) or len(url_string) == 0:
            return None
        ip_present = False
        url_string = url_string.lower()
        temp_url_string = url_string

        url_dict = {url_string: self.empty_dict.copy()}
        if tlds is None:
            _, tlds = self.get_tld()
        scheme = url_string.split('://')[0]
        if '://' in url_string and scheme not in self.schemes_and_ports.keys():
            return None
        if scheme in self.schemes_and_ports.keys():
            url_dict[url_string]['scheme'], temp_url_string = url_string.split('://')
            url_dict[url_string]['port'] = self.schemes_and_ports[url_dict[url_string]['scheme']]

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
        match len(temp):
            case 2:
                #example.org or example.org/directory
                tld_and_dir = temp[1].split('/')
                if tld_and_dir[0] in tlds:
                    url_dict[url_string]['second_level_domain'] = temp[0]
                    url_dict[url_string]['top_level_domain'] = tld_and_dir[0]
            case 3:
                tld_and_dir = temp[2].split('/')
                if tld_and_dir[0] in tlds:
                    if temp[1] in self.two_part_tlds_lhs:
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
                if tld_and_dir[0] in tlds and temp[1] in self.two_part_tlds_lhs:
                    #example.gov.bs/directory.xhtml
                    url_dict[url_string]['second_level_domain'] = temp[0]
                    url_dict[url_string]['top_level_domain'] = f"{temp[1]}.{tld_and_dir[0]}"
                elif tld_and_dir[0] in tlds:
                    #www.example.org/directory.xhtml
                    url_dict[url_string]['subdomain'] = temp[0]
                    url_dict[url_string]['second_level_domain'] = temp[1]
                    url_dict[url_string]['top_level_domain'] = tld_and_dir[0]
                else:
                    #www.bahamas.gov.bs/directory
                    temp_tld = tld_and_dir[0].split('.')
                    if temp_tld[0] in self.two_part_tlds_lhs and temp_tld[1] in tlds:
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
                url_dict[url_string]['port'] = ""
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

    def parse_url_array(self, urls: list[str], tlds: list[str] | None = None) -> dict[str, dict[str, str]] | None:
        """Parses each url in an array
        :param urls: list of urls
        :type urls: list[str]
        :return: parsed list of urls in a dictionary
        :rtype: dict[str, dict[str, str]] | None
        """
        if not urls or all(item == "" for item in urls) or not isinstance(urls, list):
            return None
        results = self._parse_url_array(urls, tlds)
        if results == None:
            return None

        url_array = {}
        for result in results:
            if result == None:
                continue
            url_array.update(result)

        if url_array == {}:
            return None
        return url_array

    def _parse_url_array(self, urls: list[str], tlds: list[str] | None = None) -> Generator[dict[str, dict[str, str]], None, None] | None:
        """Parses each url in an array
        :param urls: list of urls
        :type urls: list[str]
        :return: parsed list of urls in a dictionary
        :rtype: dict[str, dict[str, str]] | None
        """
        if not urls or all(item == "" for item in urls) or not isinstance(urls, list):
            return None
        if tlds is None:
            _, tlds = self.get_tld()
        for url in urls:
            yield self.parse_url(url, tlds)

    def to_json(self, urls: list[str] | str, prettify=True) -> str | None:
        """Creates a JSON string representation of URLs.
        :param urls: A list of URLs or a single URL string.
        :type urls: list[str] | str
        :param prettify: Whether to format the JSON output with indentation for readability.
        :type prettify: bool, optional (default is True)
        :return: A JSON string of the parsed URLs or None if the input is invalid or empty.
        :rtype: str | None
        """
        return self.shared._to_json(self.parse_url, self._parse_url_array, urls, prettify)

    def to_json_file(self, file_name: str, urls: list[str], prettify: bool=True) -> tuple[str, int]:
        """Writes parsed URLs to a JSON file.
        :param file_name: The name of the file (without extension) to write the JSON data.
        :type file_name: str
        :param urls: A list of URLs to parse and write to the file.
        :type urls: list[str]
        :param prettify: Whether to format the JSON output with indentation for readability.
        :type prettify: bool, optional (default is True)
        :return: A tuple containing the file name with extension and an int. 0 for a pass, 1 for a fail.
        :rtype: tuple[str, int]
        """
        return self.shared._to_json_file(self.parse_url, self._parse_url_array, file_name, urls, prettify)

    def to_csv(self, urls: list[str] | str) -> str | None:
        """Creates a CSV string representation of URLs.
        :param urls: A list of URLs or a single URL string.
        :type urls: list[str] | str
        :return: A CSV string of the parsed URLs or None if the input is invalid or empty.
        :rtype: str | None
        """
        return self.shared._to_csv(self.header, self.field_generator, self.parse_url, self._parse_url_array, urls)

    def to_csv_file(self, file_name, urls: list[str] | str) -> tuple[str, int]:
        """Writes parsed URLs to a CSV file.
        :param file_name: The name of the file (without extension) to write the CSV data.
        :type file_name: str
        :param urls: A list of URLs or a single URL string to parse and write to the file.
        :type urls: list[str] | str
        :return: A tuple containing the file name with extension and an int. 0 for a pass, 1 for a fail.
        :rtype: tuple[str, int]
        """
        return self.shared._to_csv_file(self.header, self.field_generator, self.parse_url, self._parse_url_array, file_name, urls)

    @cache
    def get_tld(self, path_to_tlds_file: str = 'tld.txt') -> tuple[str, list[str]]:
        """ Grabs top level domains from internet assigned numbers authority
        :param path_to_tlds_file: Path to local TLD file for fallback
        :type path_to_tlds_file: str
        :return: A tuple containing the last updated date and a list of top-level domains.
        :rtype: tuple[str, list[str]]
        """
        def get_from_iana() -> tuple[str, list[str]] | None:
            try:
                response = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt', timeout=10)
                response.raise_for_status()
                lines = response.text.split('\n')
                return lines[0], list(map(lambda x: x.lower(), filter(None, lines[1:])))
            except requests.RequestException as e:
                print(f"Error fetching TLD list: {e}")
                return None

        def get_from_local() -> tuple[str, list[str]] | None:
            try:
                with open(path_to_tlds_file, 'r') as file:
                    lines = file.readlines()
                    version = lines[1].strip()
                    dated = lines[2].strip()
                    last_updated = f"{version}, {dated}"
                    tlds = [line.strip().lower() for line in lines[4:] if line.strip()]
                    return last_updated, tlds
            except (IOError, IndexError) as e:
                print(f"Error reading local TLD file: {e}")
                return None

        # Default fallback TLDs
        fallback = ("Failed to fetch TLDs", ["com", "org", "net", "edu", "gov", "mil", "int"])
        # Try IANA first
        iana_result = get_from_iana()
        if iana_result is not None:
            return iana_result
        # Try local file next
        print(f"Retrieving locally stored TLDs from {path_to_tlds_file}")
        local_result = get_from_local()
        if local_result is not None:
            return local_result
        # Return fallback if all else fails
        print("Using fallback TLD list")
        return fallback

    def local_tld_file(self, file_name: str = 'tld') -> tuple[str, int]:
        if not isinstance(file_name, str):
            return "Failed to write file. File name must be a string.", 1
        ver_dated, tldss = self.get_tld() 
        version, dated = ver_dated.split(",")

        with open(f'{file_name}.txt', 'w') as file:
            file.write(f"File Created: {datetime.now().strftime('%d %B %Y %H:%M')}\n")
            file.write(f"{version}\n")
            file.write(f"{dated}\n\n")
            for tld in tldss:
                file.write(f"{tld}\n")
        return "File created successfully", 0

class Shared:
    def _validate_data(self, string_parse, array_parse, data) -> Generator[dict[str, dict[str, str]], None, None] | dict[str, dict[str, str]] | None:
        if not isinstance(data, str) and not isinstance(data, list):
            return None
        if isinstance(data, str) or (isinstance(data, list) and len(data) == 1):
            data = [data] if isinstance(data, str) else data
            results = string_parse(data[0])
            return results
        return None

    def _to_json(self, string_parse, array_parse, data, pretty) -> str | None:
        result = self._validate_data(string_parse, array_parse, data)
        if isinstance(data, list) and len(data) >= 2:
            result = array_parse(data)
        if isinstance(result, collections.abc.Generator):
            solution = "{\n    " if pretty is True else "{"
            first = True
            for item in result:
                key = list(item)[0]
                if first is not True:
                    solution += ",\n    " if pretty is True else ", "
                if pretty is True:
                    solution += json.dumps(key, indent=8)
                    solution += ": "
                    solution += json.dumps(item[key], indent=8)
                if pretty is False:
                    solution += json.dumps(key)
                    solution += ": "
                    solution += json.dumps(item[key])
                first = False
            solution += "\n}" if pretty is True else "}"
            return solution

        if result is None:
            return None
        if not pretty:
            return json.dumps(result)
        return json.dumps(result, indent=4)

    def _to_json_file(self, string_parse, array_parse, file_name, data, pretty) -> tuple[str, int]:
        result = self._validate_data(string_parse, array_parse, data)
        if isinstance(data, list) and len(data) >= 2:
            result = array_parse(data)
        if isinstance(result, collections.abc.Generator):
            with open(f"{file_name}.json", "w") as file:
                file.write("{\n    " if pretty is True else "{")
                first = True
                for item in result:
                    key = list(item)[0]
                    if first is not True:
                        file.write(",\n    " if pretty is True else ", ")
                    if pretty is True:
                        json.dump(key, file, indent=8)
                        file.write(": ")
                        json.dump(item[key], file, indent=8)
                    if pretty is False:
                        json.dump(key, file)
                        file.write(": ")
                        json.dump(item[key], file)
                    first = False
                file.write("\n}" if pretty is True else "}")
                return "File successfully written", 0

        if result is None:
            return "Failed to write file", 1
        if not pretty:
            with open(f"{file_name}.json", 'w') as file:
                json.dump(result, file)
        if pretty:
            with open(f"{file_name}.json", 'w') as file:
                json.dump(result, file, indent=4)
        return "File successfully written", 0

    def _to_csv(self, headers, data_fields, string_parse, array_parse, data) -> str | None:
        buffer = StringIO() #Open StringIO object
        csv_writer = csv.writer(buffer)
        csv_writer.writerow(headers)
        result = self._validate_data(string_parse, array_parse, data)
        if isinstance(data, list) and len(data) >= 2:
            result = array_parse(data)
        if isinstance(result, collections.abc.Generator):
            for full_dict in result:
                raw_input = list(full_dict)[0]
                parsed_fields = full_dict[raw_input]
                csv_writer.writerow(data_fields(raw_input, parsed_fields))
        else:
            if result is None:
                return None
            for raw_input, parsed_fields in result.items():
                csv_writer.writerow(data_fields(raw_input, parsed_fields))
        csv_data = buffer.getvalue()
        buffer.close() #Close the StringIO object
        return csv_data

    def _to_csv_file(self, headers, data_fields, string_parse, array_parse, file_name, data) -> tuple[str, int]:
        with open(f"{file_name}.csv", 'w') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(headers)
            result = self._validate_data(string_parse, array_parse, data)
            if isinstance(data, list) and len(data) >= 2:
                result = array_parse(data)
            if isinstance(result, collections.abc.Generator):
                for full_dict in result:
                    raw_input = list(full_dict)[0]
                    parsed_fields = full_dict[raw_input]
                    csv_writer.writerow(data_fields(raw_input, parsed_fields))
            else:
                if result is None:
                    return "Failed to write file", 1
                for raw_input, parsed_fields in result.items():
                    csv_writer.writerow(data_fields(raw_input, parsed_fields))
        return "File successfully written", 0

email = Email()
url = Url()

if __name__ == "__main__":
    main()
