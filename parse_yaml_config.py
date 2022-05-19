"""
ASSUMPTIONS
 - Which Env/Region to choose if NOT given in input? As that is not available in the 'common' key's value too.
 Dev
 
 - S3 using boto3 in Python has no ways of Exponential Backoff or to share upload status.
 Thus it is done by multi-threading.
 
 ---
 Reference links are mentioned towards the end.
"""
#!/usr/bin/python3
import sys,yaml,json
from collections import OrderedDict
import boto3,time
from threading import Thread

f=""
n=len(sys.argv)-1 #count of inputs might NOT require -1 depending on Python version
set_env=""
set_region=""

"""Write logic to take region and env"""
if n==3:
	set_env=sys.argv[1]
	set_region=sys.argv[2]
	f=open(sys.argv[3],'r')
elif n==2: #assuming that if there are 2 inputs then it will be region and file only. 
	set_region=sys.argv[2] #Can be modified with if case to check if input is region or env
	f=open(sys.argv[3],'r')
else:
	f=open(sys.argv[3],'r')
		

ymld=yaml.safe_load(f.read()) #loading yaml file to dict


set_env=set_env or "dev" #assumption to set "dev" as default env.
set_region=set_region or "va6" #assumption to set "va6" as default region.
out=OrderedDict() #using OrderDict, as sorted order is not maintained in dict by default.
out={"environment":set_env,"region":set_region,"configuration":OrderedDict()}
out["configuration"]["cost_center"]=ymld["metadata"]["cost_center"]
out["configuration"]["service_name"]=ymld["metadata"]["service"]
out["configuration"]["team_name"]=ymld["metadata"]["team"]


out["configuration"]["helm"]=OrderedDict()
default=ymld["common"]["helm"]["chart_name"]
out["configuration"]["helm"]["chart_name"]=ymld.get(set_env,{}).get(set_region,{}).get("helm",{}).get("chart_name",default)
default=ymld["common"]["helm"]["helm_version"]
out["configuration"]["helm"]["helm_version"]=ymld.get(set_env,{}).get(set_region,{}).get("helm_version",default)
default=ymld["common"]["helm"]["release_name"]
out["configuration"]["helm"]["release_name"]=ymld.get(set_env,{}).get(set_region,{}).get("release_name",default)
out["configuration"]["helm"]["values"]=ymld[set_env][set_region]["helm"]["values"]


out["configuration"]["notifications"]=OrderedDict()
default=ymld["common"]["notifications"]["deployments"]
out["configuration"]["notifications"]["deployments"]=ymld.get(set_env,{}).get(set_region,{}).get("notifications",{}).get("deployments",default)
default=ymld["common"]["notifications"]["releases"]
out["configuration"]["notifications"]["releases"]=ymld.get(set_env,{}).get(set_region,{}).get("notifications",{}).get("releases",default)


out["configuration"]["repo"]=OrderedDict()
default=ymld["common"]["repo"]["url"]
out["configuration"]["repo"]["url"]=ymld.get(set_env,{}).get(set_region,{}).get("repo",{}).get("url",default)
default=ymld["common"]["repo"]["version"]
out["configuration"]["repo"]["version"]=ymld.get(set_env,{}).get(set_region,{}).get("repo",{}).get("version",default)


"""PRINT JSON OUTPUT"""
jsond=json.dumps(out,indent=3)
print(jsond)


"""WRITE TO JSON FILE"""
with open("config.json","w") as outfile:
	json.dump(out,outfile,indent=3)


"""UPLOAD FILE TO S3 WITH RETRIES"""
complete=0 #flag to indicate upload status
def check_upload(): #function to wait for upload to complete in 10 min.
    time.sleep(600)
    if complete==0:
        print("S3 upload incomplete.")
        sys.exit(0) #exit without upload completion
Thread(target = check_upload).start() #starting wait thread before upload
s3 = boto3.resource('s3') #python boto3 automatically will take care of retries if upload fails within these 10 min.
s3.meta.client.upload_file('./config.json', 'config_bucket', 'config.json')
complete=1 #changing value of completion flag
sys.exit(0) #exit if code completes before 10 min.


""" CODE IS BUILT FROM SCRATCH, BUT FOLLOWING REFERENCES ARE CONSIDERED:
for s3.meta.client.upload_file
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
for confirming boto3 handles retries
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html
print json with indentation
https://stackoverflow.com/questions/12943819/how-to-prettyprint-a-json-file
"""