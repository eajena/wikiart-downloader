#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests,re
import os,time,sys
import json
import hashlib


def parse_image_info(url, pageid):
    response = requests.get(url)
    if response.status_code == 200:

        try:
            dict_info = json.loads(response.content)
            info = dict_info["query"]["pages"][str(pageid)]["imageinfo"][0]["extmetadata"]

            #print info["ObjectName"]["value"]
            #print info["Artist"]["value"]

            year = info["DateTimeOriginal"]["value"].encode("utf-8") if "DateTimeOriginal" in info else "n.a."
            return year
        except KeyError, e:
            return "n.a."
    else:
        print "Error downloading image info", url
    

def download_file(category, filename, pageid):
    sanitized_filename = filename[5:].replace(" ","_")
    m = hashlib.md5()
    m.update(sanitized_filename)
    url="https://upload.wikimedia.org/wikipedia/commons/"+m.hexdigest()[0]+"/"+m.hexdigest()[:2]+"/"+sanitized_filename

    url_info="https://commons.wikimedia.org/w/api.php?action=query&" + \
                    "prop=imageinfo&iiprop=extmetadata&" + \
                    "format=json&"+\
                    "titles=Image:"+sanitized_filename


    #print "TITLE", filename
    #if not ("ascetics" in filename):
    #    return
    
    year = parse_image_info(url_info, pageid)

    response = requests.get(url)
    if response.status_code == 200:
        f = open(os.path.join(category,sanitized_filename), 'wb')
        f.write(response.content)
        f.close()
        print "OK",sanitized_filename, year

        with open(os.path.join(category,"category.csv"), "a") as myfile:
            myfile.write(sanitized_filename+"\t"+str(year)+"\t"+url+"\n")
    else:
        print "Error downloading file", url

if __name__ == "__main__":
    if len(sys.argv)<2:
        print "Commons Downloader (Revision 2, 18.02.2016)"
        print "Error: no category given."
        print "Usage: python",sys.argv[0],"CATEGORY"
        print "  e.g. python",sys.argv[0],"Google_Art_Project_works_by_Georges_Seurat"
        sys.exit(1)
    else:
        category = "_".join(sys.argv[1:])
    
    url ="https://commons.wikimedia.org/w/api.php?action=query&"+ \
                "list=categorymembers&"+ \
                "cmtype=file&"+\
                "format=json&"+\
                "cmlimit=max&"+\
                "cmtitle=Category:"+category

    response = requests.get(url)
    if response.status_code == 200:
        dict_files = json.loads(response.content)
        num_files = len(dict_files["query"]["categorymembers"])

        if num_files==0:
            print "Error: no images in category",category
        else:
            print num_files,"files in category", category
            
            if not os.path.exists(category):
                os.makedirs(category)
            
            with open(os.path.join(category,"category.csv"), "w") as myfile:
                myfile.write("CATEGORY "+category+"\n")
                myfile.write("URL "+url+"\n")
                myfile.write("TIME "+time.strftime("%a %d.%m.%Y %H.%M")+"\n\n")
            
            for f in dict_files["query"]["categorymembers"]:
                 download_file(category, f["title"].encode('utf-8'), f["pageid"])

    #     f = open(os.path.join("images", "low", img_idx+"_"+img_id+".jpg"), 'wb')
    #     f.write(response.content)
    #     f.close()
    #     print "--",url
    else:
         print "Error", response.status_code, url
