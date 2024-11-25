# Goals
- Parse raw emails and urls from list
- Output parsed data into CSV and/or JSON file

### Future
This project will eventually become a simple project with minimal dependencies in the following languages
- Python
- Go
- Nim

## Final Table in Database Layout

| username | mail server | domain | email               |
| -------- | ----------- | ------ | ------------------- |
| example  | gmail       | com    | example@gmail.com   |
| example  | hotmail     | com    | example@hotmail.com |
| example  | outlook     | com    | example@outlook.com |

| scheme   | subdomain | second-level domain  | top-level domain | directories                                          | url                                                                            |
| -------- | --------- | -------------------- | ---------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------ |
| https    | www       | youtube              | com              | watch?v=dQw4w9WgXcQ                                  | https://www.youtube.com/watch?v=dQw4w9WgXcQ                                    |
| https    | www       | hackattic            | com              |                                                      | https://hackattic.com/                                                         |
| https    | www       | adventofcode         | com              |                                                      | https://adventofcode.com/                                                      |
| https    | home      | treasury             | gov              | services/report-fraud-waste-and-abuse/covid-19-scams | https://home.treasury.gov/services/report-fraud-waste-and-abuse/covid-19-scams |
