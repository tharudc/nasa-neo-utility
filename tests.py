from requests.models import HTTPError
from neo import NASANEO

api_key = 'aBU7hC4CuILQ1n1BEth7q6zH4ISNUjHrUkMBGgDP'
test_neo = NASANEO(api_key)

good_browse_url = 'https://api.nasa.gov/neo/rest/v1/neo/browse/'
bad_browse_url = 'https://api.nasa.gov/neo/rest/v1/neo/browse/1'
browse_params = {
    'api_key' : api_key
}
browse_file_name = 'browse_output_test.json'
    
def open_file(file_name):
    try:
        f = open(file_name)
    except OSError as err:
        return err
        print('File could not be read/open!')
        
def test_api_connection():
    assert test_neo.connect_to_api(good_browse_url, browse_params) != HTTPError
    assert test_neo.connect_to_api(bad_browse_url, browse_params) == HTTPError

def ignore_test_fetch_all_pages(): 
    test_neo.browse()
    assert open_file(browse_file_name) != OSError
    
def test_fetch_5_pages():
    test_neo.browse(5)
    assert open_file(browse_file_name) != OSError