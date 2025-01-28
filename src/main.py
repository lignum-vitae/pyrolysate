import requests

def main():
    print(parse_email('example@gmail.com'))
    print(parse_url('noaa.com/afwe?v=afwefn'))
    print(parse_url('noaa.com'))
    print(parse_url('noaa.com/afwe'))
    print(parse_url('www.noaa.com'))
    print(parse_url('www.noaa.com/directory'))
    print(parse_url('http://noaa.com/directory.txt'))
    print(parse_url('www.noaa.com/directory.txt'))
    print(parse_url('https://data.iana.org/TLD/tlds-alpha-by-domain.txt'))
    print(parse_url('https://www.bahamas.gov.bs/'))
    print(parse_url('https://guidance.data.gov.uk/publish_and_manage_data/'))

def parse_email(e_mail_string: str) -> tuple[str, str, str, str] | None:
    """ Parses email addresses into component parts
    :param e_mail_string: A string containing an email address
    :type e_mail_string: str
    :return: tuple containing email parsed into sub-parts
    :rtype: tuple[str, str, str, str]
    """
    temp = e_mail_string.split('@')
    if len(temp) != 2: 
        return #returns none for invalid emails without @
    username = temp[0]
    server_and_domain = temp[1].split('.')
    if len(server_and_domain) > 3:
        return #handles emails ending in standard tld or government emails (.gov.bs)
    mail_server = server_and_domain[0]
    domain = ".".join(server_and_domain[1:])
    return username, mail_server, domain, e_mail_string

def parse_url(url_string:str, tlds: list[str] = []) -> dict[str, str] | None:
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
        _, tlds = get_tld()
    scheme = url_string.split('://')[0]
    if not any(tld in url_string for tld in tlds) or (len([scheme]) >= 2 and scheme not in schemes):
        return
    if scheme in schemes:
        url_dict['scheme'], url_string = url_string.split('://')

    temp = url_string.split('.')
    match len(temp):
        case 2:
            #example.org
            tld_and_dir = temp[1].split('/')
            url_dict['top_level_domain'] = tld_and_dir[0] if tld_and_dir[0] in tlds else ''
            if not url_dict['top_level_domain']:
                return
            url_dict['second_level_domain'] = temp[0]
            url_dict['directories'] = "/".join(tld_and_dir[1:])
            return url_dict
        case 3:
            tld_and_dir = temp[2].split('/')
            if tld_and_dir[0] in tlds:
                if temp[1] in tlds:
                    #example.gov.bs/directory
                    url_dict['second_level_domain'] = temp[0]
                    url_dict['top_level_domain'] = ".".join([temp[1], tld_and_dir[0]])
                    url_dict['directories'] = "/".join(tld_and_dir[1:])
                    return url_dict
                #www.example.com/directory
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
                return
            url_dict['directories'] = "/".join(temp[1:])
            return url_dict
        case 4:
            tld_and_dir = ".".join(temp[2:]).split('/')
            if all(tld in tlds for tld in tld_and_dir[0].split('.')):
                #www.example.org/directory.xhtml and example.gov.bs/directory
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
    return

def get_tld() -> tuple[str, list[str]]:
    """ Grabs top level domains from internet assigned numbers authority
    :return: List of up-to-date top level domains and date list was last updated
    :rtype: tuple[str, list[str]]
    """
    response = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt')
    lines = response.text.split('\n')
    last_updated = lines[0]
    tlds = list(map(lambda x: x.lower(), filter(None, lines[1:]))) #removes empty strings from list of top level domains
    return last_updated, tlds

if __name__ == "__main__":
    main()
