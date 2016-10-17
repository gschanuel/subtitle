#!/usr/bin/python2

import struct, os, xmlrpclib, httplib
from struct import *
from xmlrpclib import Error
import argparse

parser = argparse.ArgumentParser(description='Download subtitles from opensubtitles.org')
parser.add_argument('filenames', metavar='files', type=str, nargs='+',
                   help='File(s) to search subtitles for.')
parser.add_argument('--manual', dest='manual', action='store_const',
                   const=True, default=False,
                   help='Specify to choose which subtitle to download')
parser.add_argument('--force', dest='force', action='store_const',
                   const=True, default=False,
                   help='Force downloding most downloaded subtitle if same name not found')
parser.add_argument('--skip', dest='skip', action='store_const',
                   const=True, default=False,
                   help='Skip if dont find subtitle with same filename')
args = parser.parse_args()


def hashFile(name): 
      try: 
                 
                longlongformat = 'q'  # long long 
                bytesize = struct.calcsize(longlongformat) 
                    
                f = open(name, "rb") 
                    
                filesize = os.path.getsize(name) 
                hash = filesize 
                    
                if filesize < 65536 * 2: 
                       return "SizeError" 
                 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
                f.seek(max(0,filesize-65536),0) 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
                f.close() 
                returnedhash =  "%016x" % hash 
                return returnedhash 
    
      except(IOError): 
                return "IOError"

def download(*args):
        try:
                subFileName = os.path.basename(MovieFile)[:-4] + "_"+ lang + "." + moviesList['data'][int(resp)]['SubFileName'][-3:]
                subURL = moviesList['data'][int(resp)]['SubDownloadLink']
                print '    Downloading ' + lang + ' ' + str(resp) + ' -> ' + moviesList['data'][int(resp)]['SubFileName']
                response = os.system('wget -q -O - ' + subURL + ' | gunzip  > "' + subFileName + '"' )
                #print 'wget -O - ' + subURL + ' | gunzip  > "' + subFileName + '"'
                if response != 0:
                        print "    An error ocurred " + response
        except(IOError):
                return "    Hash error"

# ================== Main program ========================


server = xmlrpclib.Server('http://api.opensubtitles.org/xml-rpc')


langs = ['pob','eng']
#langs = ['pob']
for MovieFile in args.filenames:
        print MovieFile
        try:
            myhash = hashFile(MovieFile)
            size = os.path.getsize(MovieFile)
            session =  server.LogIn("","","en","OSTestUserAgent")
            #print myhash
            #print size
            #print session
    
            token = session["token"]
            for lang in langs:
                    HighDownloads = 0
                    searchlist = []
                    searchlist.append({'sublanguageid':lang,'moviehash':myhash,'moviebytesize':str(size)})
                    moviesList = server.SearchSubtitles(token, searchlist)
                    #print moviesList
                    #print moviesList['data']
                    resp='a'
                    if moviesList['data']:
                        for i in range(len(moviesList['data'])):
                                item=moviesList['data'][i]['SubFileName'][:-4]
                                if (MovieFile[:-4]) == item:
                                        resp = i
                                if (moviesList['data'][i]['SubDownloadsCnt'] > moviesList['data'][HighDownloads]['SubDownloadsCnt']):
                                        HighDownloads = i
                        if (resp != 'a') and (not args.manual):
                                download()
                        else:
                                if (args.force):
                                        resp = HighDownloads
                                        download()
                                else:
                                        if (not args.skip):
                                                mindex = 0
                                                for item in moviesList['data']:
                                                        print "    " + str(mindex) + ' - ' + item['SubFileName'] + " (" + item['SubDownloadsCnt'] +")"
                                                        mindex = mindex + 1
                                                if mindex > 1:
                                                        resp = input("    Select a subtitle in " + lang + ": ") 
                                                        mindex = 0
                                                else:
                                                        resp = 0
                                                if (resp < len(moviesList['data'])):
                                                        download()
                                                else:
                                                        print '    Skiping'

                    else:
                        print "No subtitles found in " + lang
            
            server.Logout(session["token"])
        except Error, v:
            print "An error ocurred"
