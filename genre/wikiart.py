#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests,re
import os,time,sys
import json
import hashlib


def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        f = open(filename, 'wb')
        f.write(response.content)
        f.close()
        print "OK", filename

        #with open(os.path.join(category,"category.csv"), "a") as myfile:
        #    myfile.write(sanitized_filename+"\t"+str(year)+"\t"+url+"\n")
    else:
        print "Error downloading file", url


if __name__ == "__main__":
    folder = sys.argv[1]
    style = sys.argv[2]

    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(os.path.join(folder,style)):
        os.makedirs(os.path.join(folder,style))
    
    columns = ["artistName","image","title","year","width","height"]
    with open(os.path.join(folder, style+".csv"), "w") as myfile:
        myfile.write(",".join(["style","filename"] + columns)+"\n")

        page = 1
        while 0<page:
            # all
            if folder=="featured":
                url="https://www.wikiart.org/en/paintings-by-genre/%s?select=featured&json=2&page=%d" % (style, page)
            else:
                url="https://www.wikiart.org/en/paintings-by-genre/%s?json=2&page=%d" % (style, page)
            # featured
            response = requests.get(url)
            if response.status_code == 200:
                dict_files = json.loads(response.content)
                print "Page %d, %d paintings total" % (page, dict_files["AllPaintingsCount"])

                if dict_files["Paintings"] is None:
                    page = 0
                else:
                    for p in dict_files["Paintings"]:
                        p["year"] = str(p["year"])
                        p["width"] = str(p["width"])
                        p["height"] = str(p["height"])
                        filename = "%s-%s" % (p["artistName"].encode('utf-8').strip(), os.path.basename(p["image"].encode("utf-8").strip()))
                        myfile.write(",".join([style, filename] + ['"'+p[c].encode('utf-8').strip()+'"' for c in columns])+"\n")
                        download_file(p["image"], os.path.join(folder,style,filename))
                    page+=1
            else:
                 print "Error", response.status_code, url
