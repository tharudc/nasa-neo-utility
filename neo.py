import requests
import json
import calendar
import pprint as pp

from requests.exceptions import HTTPError
from datetime import datetime, date, timedelta
from calendar import Calendar

class NASANEO:
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.response = None
        self.response_text = None
        self.response_json = None
        
        self.browse_data = []
        self.total_elements = 0
        self.total_pages = 0
        self.curr_page = 0
        
        self.feed_data = []
        self.dates_dict = {}
        
    def connect_to_api(self, connection_string, params):
        '''
        Connects to NASA's API given a connection string and parameters.
        Determine success or error in connecting. 
        Store response body text and as json
        '''
        try: 
            self.response = requests.get(connection_string, params)
            self.response.raise_for_status()
            self.response_text = self.response.text
            self.response_json = self.response.json()
        except HTTPError as http_error:
            print(f'HTTPError occured: {http_error}')
            return HTTPError
        except Exception as err:
            print(f'Other error occured: {err}')
            return Exception
        else:
            print(f'Successfully connected to: {connection_string}!')
            return True
            
    def get_closest_approach(self):
        '''
        Function that strips down asteroid's closest_approach_data array 
        to have only the closest approach. Closeset approach is calculated
        based on the minimum astronomical distance.
        '''
        miss_distances = []
        new_data = []
        for asteroid in self.browse_data:
            for data in asteroid['close_approach_data']:
                miss_distances.append(float(data['miss_distance']['astronomical']))
            min_distance_index = miss_distances.index(min(miss_distances))
            new_data = asteroid['close_approach_data'][min_distance_index]
            asteroid['close_approach_data'] = new_data
            miss_distances = new_data = []
            
    def browse(self, page_num=None, file_name='browse_output_test.json'):
        '''
        Function to ...
        
        @page_num Page number to read up to (Pages start from 0)
        '''
        params = {
            'api_key' : self.api_key
        }
        connection_string = 'https://api.nasa.gov/neo/rest/v1/neo/browse/'
        self.connect_to_api(connection_string, params)
        try:
            self.browse_data = self.response_json['near_earth_objects']
            self.total_pages = int(self.response_json['page']['total_pages'])
            self.curr_page = int(self.response_json['page']['number'])
            self.total_elements += int(self.response_json['page']['size'])
        except:
            print('Something went wrong!')
            return False
        finally:
            if page_num == None: page_num = self.total_pages 
            else: page_num = page_num - 1
            
            while int(self.response_json['page']['number']) <= page_num:
                next_url = self.response_json['links']['next']
                self.connect_to_api(next_url, params)
                self.browse_data.extend(self.response_json['near_earth_objects'])
                self.total_elements += int(self.response_json['page']['size'])
                
            self.get_closest_approach()
            self.write_to_file(self.browse_data, file_name)
            return True
        
    def month_date_validation(self, start_date, end_date):
        try:
            start_year = start_date.year
            start_month = start_date.month
            end_year = end_date.year
            end_month = end_date.month
        except Exception as err:
            print(err)
            return False # Right way to implement this?
        finally:
            mr = calendar.monthrange(start_year, start_month)
            if start_date + timedelta(days=mr[1]-1) == end_date:
                return [start_date, end_date]
            else:
                print(f'Correcting: {start_date, start_date + timedelta(days=mr[1])}')
                return [start_date, start_date + timedelta(days=mr[1])]
        
    def feed(self, start_date, end_date):
        connection_string = 'https://api.nasa.gov/neo/rest/v1/feed'
        # Check if provided dates are valid
        valid_dates = self.month_date_validation(date.fromisoformat(start_date), date.fromisoformat(end_date))
        start = valid_dates[0]
        end = valid_dates[1]
        r = calendar.monthrange(start.year, start.month)[1] % 7
        curr = start
        while curr.day + 7 <= end.day:
            self.dates_dict[curr] = curr + timedelta(days=6)
            params = {
                'api_key' : self.api_key,
                'start_date' : curr.strftime('%Y-%m-%d'),
                'end_date' : (curr + timedelta(days=6)).strftime('%Y-%m-%d')
            }
            self.connect_to_api(connection_string, params)
            print(curr, curr + timedelta(days=6))
            self.feed_data.append(self.response_json['near_earth_objects'])
            curr = curr + timedelta(days=7)
        # Do remaining date range
        self.dates_dict[curr] = curr + timedelta(days=r-1)
        params = {
            'api_key' : self.api_key,
            'start_date' : curr.strftime('%Y-%m-%d'),
            'end_date' : (curr + timedelta(days=r-1)).strftime('%Y-%m-%d')
        }
        self.connect_to_api(connection_string, params)
        self.feed_data.extend(self.response_json['near_earth_objects'])   
        self.write_to_file(self.feed_data, 'feed_output_1.json')       
    
    def lookup(self, asteroid_id):
        params = {
            'api_key' : self.api_key,
            'asteroid_id' : asteroid_id
        }
        connection_string = 'https://api.nasa.gov/neo/rest/v1/neo/'

        self.connect_to_api(connection_string, params)
  
    def write_to_file(self, data, file_name, mode='w'):
        try:
            with open(file_name, mode) as f:
                f.write(json.dumps(data, indent=4))
        except IOError:
            print('An error occured writing to file!')
            
if __name__ == '__main__':
    
    api_key = 'aBU7hC4CuILQ1n1BEth7q6zH4ISNUjHrUkMBGgDP'
    neo = NASANEO(api_key)
    start_date = '2021-09-01'
    end_date = '2021-09-30'
    
    #neo.browse(2)
    neo.feed(start_date, end_date)