from urllib2 import urlopen
try:
    from  xml.etree.ElementTree import ElementTree as ET # Python >= 2.5
except ImportError:
    try:
        from elementtree.ElementTree import ElementTree as ET
    except ImportError:
        raise Exception("ElementTree is required")
    
from constants import METRO_API_URL,CARRIERS_ENDPOINT

class Service(object):
    """A utility class for handling calls to the webservice and returning the response as an ElementTree"""

    def get_service_data(self,service,api_key):
        """"Makes a call to a webservice endpoint and returns the result as an ElementTree"""
        response = urlopen("%s/%s?api_key=%s" % (METRO_API_URL,service,api_key))
        et = ET()
        et.parse(response)
        return et

class Carriers(Service):
    """The list of all Metro passenger carrier agencies"""
    
    def __get__(self,obj,objtype):
        if not hasattr(self,'_items'):
            data = self.get_service_data(CARRIERS_ENDPOINT,obj.api_key)
            carriers = data.find('carriers')
            results = []
            for carrier in carriers.findall('item'):
                item_id = carrier.find('id').text
                item_text = carrier.find('text').text
                item_code = carrier.find('code').text
                results.append(Carrier(int(item_id),item_text,item_code))
            setattr(self,'_items',results)
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
    http://developer.metro.net/docs/carriers/
    """
    def __init__(self,id,name,code):
        self.id = id
        self.name = name
        self.code = code
        
    routes = Routes()
    
    def __repr__(self):
        return "<Carrier: %s>" % self.name
    def __unicode__(self):
        return u"%s:%s:%s" % (self.id,self.name,self.code)
    def __str__(self):
        return self.__unicode__()

class Routes(object):
    """
    http://developer.metro.net/docs/routes/
    """
    pass

class Route(object):
    pass


class MetroAPI(object):
    """
    The object responsible for communicating with the Metro API
    """
    
    def __init__(self,api_key):
        self.api_key = api_key
        
    carriers = Carriers()    