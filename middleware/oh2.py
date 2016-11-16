import urllib.request
import json

addr = "http://127.0.0.1:8080"
rest_path = "/rest"
items_path = rest_path + "/items"

def SetAddr(new_addr):
  global addr
  addr = "http://" + new_addr

def GetRequest(url):
  return json.loads(urllib.request.urlopen(url).read().decode("utf-8"))

def PostRequest(url, data):
  req = urllib.request.Request(url, data.encode(), {"Content-Type": "text/plain"})
  urllib.request.urlopen(req)

def GetItems():
  global addr
  global items_path
  url = addr + items_path
  return GetRequest(url)

def GetItem(item):
  global addr
  global items_path
  url = addr + items_path + "/" + item
  return GetRequest(url)

def SetItem(item, command):
  global addr
  global items_path
  url = addr + items_path + "/" + item
  PostRequest(url, command)

