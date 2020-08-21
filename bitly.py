#! /usr/bin/python3

import requests

def shorten_url(long_url):
    '''
    This function utilizes 'Bitly's API to convert long URLs into short 'bit.ly' URLs.
    On success, this function will return the shortened URL.
    On failure, this function will return the URL that was given, without change.
    '''
    header = {
        "Authorization": "Bearer <YOUR BITLY API GENERIC ACCESS TOKEN>",
        "Content-Type": "application/json"
    }
    params = {
        "long_url": long_url
    }
    
    response = requests.post("https://api-ssl.bitly.com/v4/shorten", json = params, headers = header)
    data = response.json()

    try:
        short_url = data['link']
        return short_url

    except:
        return long_url
