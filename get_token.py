from __future__ import print_function
import time
import meli
from meli.rest import ApiException
from pprint import pprint
# Defining the host, defaults to https://api.mercadolibre.com
# See configuration.py for a list of all supported configuration parameters.
configuration = meli.Configuration(
    host = "https://api.mercadolibre.com"
)


# Enter a context with an instance of the API client
with meli.ApiClient() as api_client:
# Create an instance of the API class
    api_instance = meli.OAuth20Api(api_client)
    grant_type = 'authorization_code' # str
    client_id = '6545766642471155' # Your client_id
    client_secret = 'TnkpxGW9LnCbaYrnGvetdZ2lfj3udxjE' # Your client_secret
    redirect_uri = 'http://localhost:3000' # Your redirect_uri
    code = 'TG-5ff895e87b919100066e756a-657456460' # The parameter CODE
    refresh_token = 'refresh_token_example' # Your refresh_token

try:
    # Request Access Token
    api_response = api_instance.get_token(grant_type=grant_type, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, code=code)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OAuth20Api->get_token: %s\n" % e)