#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header  = data.split('\r\n\r\n')[0]
        code = int(header.split()[1])
        return code
       

    def get_headers(self,data):
        #we use the \r\n\r\n to split the headers and body
        headers = data.split('\r\n\r\n')[0]
        return headers
        

    def get_body(self, data):
        try:
            body = data.split('\r\n\r\n')[1]
            return body
        except:
            return ""
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    #ref:https://docs.python.org/3/library/urllib.parse.html
    def GET(self, url, args=None):
        code = 500
        body = ""
        if (len(url)!= 0):
            url_split = urllib.parse.urlparse(url)
            host = url_split.hostname
            port = url_split.port 
            if port==None:
                port = 80
            self.connect(host,port)
        
            path = url_split.path
            if path =='':
                path = '/'

            query = url_split.query
            if (query != ''):
                path += "?" + url_split.query
            
            inf_send = ("GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, host))
            
            
            self.sendall(inf_send)
            server_re = self.recvall(self.socket)

            code = self.get_code(server_re)
            body = self.get_body(server_re)
            print("Status code:",code)
            print("Body:")
            print(body)
            self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        if (len(url)!= 0):
            url_split = urllib.parse.urlparse(url)
            host = url_split.hostname
            port = url_split.port 
            if port==None:
                port = 80
            self.connect(host,port)
        
            path = url_split.path
            if path =='':
                path = '/'

            query = url_split.query
            if (query != ''):
                path += "?" + url_split.query

            inf_send = "POST %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n" % (path, host)
    
            if args==None: #deal without args
                inf_send += ("Content-Length: 0\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n")
            else:
                body_str = ""
                for key_p in args.keys():
                    body_str += key_p + "=" + args[key_p] + "&"
                #all but the last & since end of key value pair 
                body_str = body_str[0:len(body_str)-1]
                body_len = len(body_str) 

                #deal with the body
                inf_send += ("Content-Length: %d\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n" % body_len )
                inf_send += body_str

        
            self.sendall(inf_send)
            server_re = self.recvall(self.socket)

            code = self.get_code(server_re)
            body = self.get_body(server_re)
            print("Status code:",code)
            print("Body:")
            print(body)
            self.close()

            

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
