#!/usr/bin/env python

import sys
import argparse
import os
import gubble


# Accept command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description='Gubble server', 
        allow_abbrev=False)

    default_port = 5000
    parser.add_argument('port',
                        type=int,
                        default=default_port,
                        nargs='?',
                        help='the port at which the server should listen')
    return parser


# Accept command line arguments and run app.py
def main():
    try:
        parser = parse_args()
        args = parser.parse_args()
        port = args.port

        try:
            # Build css file
            #os.chdir('./static/')
            #os.system('npm run css-build')
            #os.system('npm run start')
            os.chdir('.')
            gubble.app.run(host='0.0.0.0', port=port, debug=True)
        except Exception as ex:
            print(ex, file=sys.stderr)
            sys.exit(1)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()