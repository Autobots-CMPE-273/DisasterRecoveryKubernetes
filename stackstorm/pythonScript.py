import json
import urllib2
import pickle
import requests
import time

data = urllib2.urlopen('http://52.202.104.27:8080/api/v1/nodes')
json_string = data.read()
parsed_json = json.loads(json_string)

#print(parsed_json)


def check():

    #print("In check")

    dictFile = open("/DictObject.txt","rb")
    dictObj = pickle.load(dictFile)
    dictFile.close()

    for entry in parsed_json['items']:
        #dictObj = {}
        #dictObj = pickle.load(dictFile)

        #print(dictObj)

        print('**************************************************')
        print(entry['status']['conditions'][0]['status'])
        
        if entry['status']['conditions'][0]['status'] == 'Unknown':
	    if entry['metadata']['name'] in dictObj.keys():
	        if dictObj[entry['metadata']['name']] == 'True':
	    	    #dictObj[entry['metadata']['name']] = entry['status']['conditions'][0]['status']
	            url = 'http://localhost:9101/v1/webhooks/AWSCreate'
	    	    data = {'trigger': 'aws.create_vm','payload': {'attribute1': entry['metadata']['name']}}
	    	    headers = {'content-type': 'application/json', 'X-Auth-Token': 'matoken'}
		    
  	    	    r = requests.post(url, data=json.dumps(data), headers=headers)
		    print(r)
	    	    dictObj[entry['metadata']['name']] = 'Processing...'

            	    
	    else:
		url = 'http://localhost:9101/v1/webhooks/AWSCreate'
		data = {'trigger': 'aws.create_vm','payload': {'attribute1': entry['metadata']['name']}}
		headers = {'content-type': 'application/json', 'X-Auth-Token': 'matoken'}

		r = requests.post(url, data=json.dumps(data), headers=headers)
		dictObj[entry['metadata']['name']] = 'Processing...'
        else:
	    dictObj[entry['metadata']['name']] = entry['status']['conditions'][0]['status']
    

    check = open("/CheckLog.log", "wa")
    check.write(str(dictObj))
    dictFile = open("/DictObject.txt","wb")
    pickle.dump(dictObj, dictFile)
    dictFile.close()

#check()

i=1

while i != 5:
    #print(i)
    check()
    i = i + 1
    time.sleep(15)
				
