import json,urllib, ssl
import xmltodict as xmlconverter

# load config from a JSON file (or anything outputting a python dictionary)
with open("/var/www/ElRoiApp/ElRoiApp/roi.webserver.conf") as f:
    config = json.load(f)

def get_external_id(firstname, lastname):
    externalid = ""
    # CCB INTEGRATION
    data = {}
    url = config['ccb']['base_url']
    srv = config['ccb']['srv_search_member']
    base64string = config['ccb']['baseAuth']
    api_url = url + srv + 'last_name={}&first_name={}'.format(lastname, firstname)
    #print("URL"+ api_url)
    context = ssl._create_unverified_context()
    req = urllib.request.Request(api_url)
    req.add_header("Authorization", "Basic %s" % base64string) 
    xmlresponse = urllib.request.urlopen(req, context=context)
   
    jsondata = xmlconverter.parse(xmlresponse.read().decode('utf-8'))
    # throw keyError if there is no response
    try:
        #print(jsondata['ccb_api']['response']['individuals'])
        loopcount = int(jsondata['ccb_api']['response']['individuals']['@count'])
        if(loopcount > 1):
            for x in range(loopcount):
                externalid = jsondata['ccb_api']['response']['individuals']['individual'][x]['@id']
                #print('External id : '+ externalid)
        else:
            externalid = jsondata['ccb_api']['response']['individuals']['individual']['@id']
            #print('One External id'+ externalid)
    except KeyError:
        pass
    xmlresponse.close()
    return externalid

def record_attendance_external_id(externalid):
    # CCB INTEGRATION
    url = config['ccb']['base_url']
    srv = config['ccb']['srv_add_attendance']
    base64string = config['ccb']['baseAuth']
    api_url = url + srv + 'individual_id={}'.format(externalid)
    #print("Attendance URL"+ api_url)
    context = ssl._create_unverified_context()
    req = urllib.request.Request(api_url)
    req.add_header("Authorization", "Basic %s" % base64string) 
    xmlresponse = urllib.request.urlopen(req, context=context)
   
    jsondata = xmlconverter.parse(xmlresponse.read().decode('utf-8'))
    # throw keyError if there is no response
    try:
        #print(jsondata['ccb_api']['response']['individuals'])
        loopcount = int(jsondata['ccb_api']['response']['individuals']['@count'])
        if(loopcount == 1):
            externalid = jsondata['ccb_api']['response']['individuals']['individual']['@id']
            print('Attendance id'+ externalid)
    except expression as identifier:
        pass

    xmlresponse.close()
    return externalid
