import os
from urllib import urlencode
from urllib2 import urlopen
try:
    from  xml.etree.ElementTree import ElementTree as ET # Python >= 2.5
except ImportError:
    try:
        from elementtree.ElementTree import ElementTree as ET
    except ImportError:
        raise Exception("ElementTree is required")
    
from constants import METRO_API_URL,CARRIERS_ENDPOINT,ROUTES_ENDPOINT

class Service(object):
    """A utility class for handling calls to the webservice"""

    def __init__(self,item_type,list_elem,fields):
        self.list_elem = list_elem
        self.fields = fields
        self.item_type = item_type

    def get_service_data(self,service,**kwargs):
        """"
        Makes a call to a webservice endpoint and extracts the relevant fields into
        instances of the item type for the collection
        """
        #TODO memoization broken, needs to account for args
        if not hasattr(self,'_items'):
            url_base = "%s/%s" % (METRO_API_URL,service)
            params = {'api_key':MetroAPI.api_key}
            if len(kwargs):
                params.update(kwargs)
            qs = urlencode(params)
            url = "%s?%s" % (url_base,qs)
            print url
            response = urlopen(url)
            et = ET()
            et.parse(response)
            count = et.find('metadata').find('records_found')
            results = []
            
            if int(count.text) > 0:
                items = et.find(self.list_elem)
                for item in items.findall('item'):
                    item_args = {}
                    for field in self.fields:
                        item_args.update({field:item.find(field).text})
                    results.append(self.item_type(**item_args))
            setattr(self,'_items',results)
        return self._items
    
class Routes(Service):
    """
    Routes offered for a particular Metro affiliate carrier
    http://developer.metro.net/docs/routes/
    """
    
    def __get__(self,obj,objtype):
        self.get_service_data(ROUTES_ENDPOINT,carrier=obj.id)
        return self
    
    #TODO DRY
    def __repr__(self):
        return repr(self._items)
    def __len__(self):
        return len(self.get())
    def __getitem__(self,k):
        return self._items[k]
    def __contains__(self,elt):
        return elt in self._items

class Route(object):
    
    def __init__(self,id,text,direction):
        self.id = int(id)
        self.text = text
        self.direction = direction

class Carriers(Service):
    """
    The list of all Metro passenger carrier agencies
    
    http://developer.metro.net/docs/carriers/
    """
    
    def __get__(self,obj,objtype):
        self.get_service_data(CARRIERS_ENDPOINT)
        return self
    
    def __repr__(self):
        return repr(self._items)
    def __len__(self):
        return len(self.get())
    def __getitem__(self,k):
        return self._items[k]
    def __contains__(self,elt):
        return elt in self._items
    
    def get(self,id=None,code=None):
        """
        Used for selecting specific Carrier instances. It is assumed that both
        id and code are unique. Only one of the keyword arguments will be
        used in the lookup.
        
        id  -  The carrier ID
        code - A two-letter code associated with the carrier
        
        If no parameters are supplied, the entire list is returned.
        If no Carrier is found matching the search criteria, None is returned.
        """
        if id is None and code is None:
            return self._items if len(self._items) else []
        for carrier in self._items:
            if id and carrier.id == id:
                return carrier
            elif code and carrier.code == code:
                return carrier
        return None
    
    
class Carrier(object):
    """
    Represents a carrier
    """
    def __init__(self,id,text,code):
        self.id = int(id)
        self.text = text
        self.code = code
        
    routes = Routes(Route,'routes',['id','text','direction'])
    
    def __repr__(self):
        return "<Carrier: %s>" % self.text
    def __unicode__(self):
        return u"%s:%s:%s" % (self.id,self.text,self.code)
    def __str__(self):
        return self.__unicode__()

class MetroAPI(object):
    """
    The object responsible for communicating with the Metro API
    
    #this doctest assumes that you have set the API key
    #using either the environment or a file in your home dir.
    >>> from metro.api import MetroAPI
    >>> metro = MetroAPI()
    >>> metro.carriers
    """
    api_key = None
    
    def __init__(self,api_key=None):
        
        if (api_key is None or not len(api_key)) and self.api_key is None:
            raise Exception(
                """
                You need to supply an API key. 
                If you  do not have one, you'll need to register for an account at
                http://developer.metro.net/
                """)
        self.__class__.api_key = api_key
        
    def _routes(self,carrier):
        return carrier.routes
    
    carriers = Carriers(Carrier,'carriers',['id','text','code'])
    routes = _routes
    
def initialize_api():
    #check for the API key:
    # 1. as the environment variable METRO_API_KEY
    # 2. as the only text in the file $HOME/.metro_api_key
    if 'METRO_API_KEY' in os.environ:
            MetroAPI.api_key = os.environ['METRO_API_KEY']
    else:
        try:
            #TODO clunky
            home =  os.environ['HOME'] if 'HOME' in os.environ else '~'
            f = open('%s/.metro_api_key' % home, 'r')
            MetroAPI.api_key = f.readline().strip()
            f.close()
        except:
            MetroAPI.api_key = ''
            
   
    
    