import pprint
import apiclient
import os

DEVELOPER_KEY = str(os.environ.get('google_DEVELOPER_KEY', ''))
def main():
    service = apiclient.discovery.build("customsearch", "v1",developerKey=DEVELOPER_KEY)

    res = service.cse().list(
        q='lectures',
        cx='017576662512468239146:omuauf_lfve',
    ).execute()
    pprint.pprint(res)


if __name__ == '__main__':
    main()
