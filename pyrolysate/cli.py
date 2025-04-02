import argparse
from pathlib import Path
from pyrolysate import url, email, parse_input_file

def main():
    parser = argparse.ArgumentParser(prog= 'pyrolysate', usage ='%(prog)s [options]')
    parser.add_argument('target', type = str, nargs = '*', default = None, help = 'An email or URL string, or a list of email or URL strings.')
    parser.add_argument('-u', '--url', action = 'store_true', help = 'Specify URL input.')
    parser.add_argument('-e', '--email', action = 'store_true',  help = 'Specify Email input.')
    parser.add_argument('-i', '--input_file', type = str, default = None, help = 'Input file name with extension.')
    parser.add_argument('-o', '--output_file', type = str, default = None, help = 'Output file name without extension.')
    parser.add_argument('-c', '--csv', action = 'store_true',  help = 'Save output file as JSON.')
    parser.add_argument('-j', '--json', action = 'store_true',  help = 'Save output file as CSV.')
    parser.add_argument('-np', '--no_prettify', action = 'store_false',  help = 'Turn off prettified JSON output')
    parser.add_argument('-d', '--delimiter', type = str, default = '\n', help = 'The delimiter to use. Only valid when --input is provided.')
    args = parser.parse_args()
    print(args)

    # Initialize the handler based on input type
    handler = url if args.url else email

    # Get input data
    if args.input_file:
        if not Path(args.input_file).is_file():
            raise FileNotFoundError(f"Input file not found: {args.input_file}")
        data = parse_input_file(args.input_file, delimiter=args.delimiter)
    else:
        data = args.target

    # Handle empty input
    if not data:
        raise ValueError("No input provided. Use positional arguments or --input_file")

    # Process the data and determine output format
    if args.output_file is not None:
        # Determine file extension and path
        if args.json is True:
            extension = ".json"
        elif args.csv is True:
            extension = ".csv"
        else:
            extension = ".txt"

        output_path = Path(f"{args.output_file}{extension}")
        if output_path.exists():
            raise FileExistsError(f"Output file already exists: {output_path}")

        # Process and save output
        if args.json:
            handler.to_json_file(args.output_file, data) if args.no_prettify is True else handler.to_json_file(args.output_file, data, prettify=False)
        elif args.csv:
            handler.to_csv_file(args.output_file, data)
        else:
            # Default to txt file
            with open(f"{args.output_file}.txt", 'w') as file:
                file.write(str(handler.parse_url_array(data) if args.url else handler.parse_email_array(data)))
        print(f"Output written to {output_path}")
    # Output to console
    elif args.output_file is None:
        if args.json:
            output = handler.to_json(data) if args.no_prettify is True else handler.to_json_file(args.output_file, data, prettify=False)
        elif args.csv:
            output = handler.to_csv(data)
        else:
            output = handler.parse_url_array(data) if args.url else handler.parse_email_array(data)
        print(output)

if __name__ == "__main__":
    main()
