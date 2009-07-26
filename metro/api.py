from urllib2 import urlopen
from xml.etree.ElementTree import ElementTree
from constants import METRO_API_URL,CARRIERS_ENDPOINT

class Metro(object):
    """
    The object responsible for communicating with the Metro API
    """
    
    def __init__(self,api_key):
        self.api_key = api_key
        
    def _get_url(self,service):
        response = urlopen("%s/%s?api_key=%s" % (METRO_API_URL,service,self.api_key))
        
        return response
        
    def _get_service_data(self,service):
        cache_name = '%s_cache' % service.replace('.','').replace('/','')
        if hasattr(self,cache_name):
            print 'returning from cache'
            return getattr(self,cache_name)
        else:
            response = self._get_url(service)
            et = ElementTree()
            et.parse(response)
            setattr(self,cache_name,et)
            return et
        
    def carriers(self,id=None,code=None):
        results = []
        response = self._get_service_data(CARRIERS_ENDPOINT)
        
        carriers = response.find('carriers')
        for carrier in carriers.findall('item'):
            item_id = carrier.find('id').text
            item_text = carrier.find('text').text
            item_code = carrier.find('code').text
            c = Carrier(item_id,item_text,item_code)
            if id and item_id == str(id):
                return c
            elif code and code == item_code:
                return c
            else:
                results.append(c)
        return results
    
    def routes(self,carrier):
        """
        Lookup the routes for a Metro carrier
        """
        pass
    
class Carrier(object):
    """
    Represents a carrier
    http://developer.metro.net/docs/carriers/
    """
    def __init__(self,id,name,code):
        self.id = id
        self.name = name
        self.code = code
        
    def __unicode__(self):
        return u"%s:%s:%s" % (self.id,self.name,self.code)
        
    def __str__(self):
        return self.__unicode__()

class Route(object):
    """
    http://developer.metro.net/docs/routes/
    """
    pass
        
if __name__ == '__main__':
    metro = Metro('55bea475-703c-493e-8586-7c00e48b2b1b')
    carriers = metro.carriers()
    for carrier in carriers:
        print carrier
    foothill = metro.carriers(id=23)
    print foothill.name