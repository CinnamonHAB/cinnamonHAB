import urllib.request
import json

addr = "http://127.0.0.1:8080"
rest_path = "/rest"
items_path = rest_path + "/items"

# Sets a new address to send requests to. Provide an IP/domain with a port, without the protocol.
# Protocol gets automatically added. Does not return anything. Default is 127.0.0.1,
# Example: SetAddr("192.168.0.22:1337").
def SetAddr(new_addr):
  global addr
  addr = "http://" + new_addr

# Sends a GET HTTP request to OpenHab on the given URL.
# If all goes well, returns whatever OpenHAB returned, interpreted as JSON.
# If something goes wrong, returns {"error":400} (but using the real code that it got).
def _GetRequest(url):
  try:
    res = urllib.request.urlopen(url)
  except urllib.error.HTTPError as err:
    return {"error":err.code}
  else:
    return json.loads(res.read().decode("utf-8"))

# Sends a POST HTTP request to OpenHAB on the given URL with the given data in the body.
# If all goes well returns {}.
# If something goes wrong, returns {"error":400} (but using the real code that it got).
def _PostRequest(url, data):
  req = urllib.request.Request(url, data.encode(), {"Content-Type": "text/plain"})
  try:
    res = urllib.request.urlopen(req)
  except urllib.error.HTTPError as err:
    return {"error":err.code}
  else:
    return {}

# Gets all items from OpenHAB. 
# If all goes well returns [{...}. {...}, ...], where each {...} is an item as in the
# GetItem(item) method.
# If something goes wrong, returns {"error":400} (but using the real code that it got).
def GetItems():
  global addr
  global items_path
  url = addr + items_path
  return _GetRequest(url)

# Gets an item from OpenHAB. 
# If all goes well returns something like
# {
#  "link": "http://localhost:8080/rest/items/l1",
#  "state": "100",
#  "type": "Dimmer",
#  "name": "l1",
#  "label": "Light 1",
#  "tags": [],
#  "groupNames": [
#    "sg1"
#  ]
# }
# If something goes wrong, returns {"error":400} (but using the real code that it got).
def GetItem(item):
  global addr
  global items_path
  url = addr + items_path + "/" + item
  return _GetRequest(url)

# Sends a command to OpenHAB for the specifid item.
# If all goes well returns {}.
# If something goes wrong, returns {"error":400} (but using the real code that it got).
def SetItem(item, command):
  global addr
  global items_path
  url = addr + items_path + "/" + item
  return _PostRequest(url, command)

# Returns all items from the given group.
# If all goes well returns something like
# {
#   "item1": "type",
#   "item2": "type",
#   "item3": "type"
# }
def _GetItemNamesDict(item):
  items = {}
  if item["type"] != "Group":
    items[item["name"]] = item["type"]
  else:
    for v in item["members"]:
      items.update(_GetItemNamesDict(v))

  return items

# Gets a problem text for the specified group and the target state.
# Target state will be copied as given to the problem text.
def GetProblem(group_name, target_state):
  group = GetItem(group_name)
  if ("error" in group):
    return "error " + str(group["error"])

  items = _GetItemNamesDict(group)
  item_names = [key for key in items]
  item_types_names = ["(" + items[key] + " " + key + ")" for key in items]
  item_names_group = ["(IN " + key + " " + group_name + ")" for key in items]
  item_states = [("(not " if GetItem(key)["state"] == "OFF" else " " ) + "(ON " + key + ")" + ("(not " if GetItem(key)["state"] == "OFF" else " ") for key in items]
  problem = "(define (problem problem-name) (:domain cinnemain) (:objects "
  problem += " ".join(item_names)
  problem += ") (:init " + " ".join(item_types_names)
  problem += " (GROUP " + group_name + ") "
  problem += " ".join(item_names_group)
  problem += " ".join(item_states)
  problem += target_state + "))"
  return problem

# Just a wrapper for file printing. In this case used to print problem files.
def WriteProblem(problem):
  with open("problem.pddl", "w") as problem_file:
    print(problem, file=problem_file)

# VERY UGLY!!!
# TODO: LSTRZ
# NEEDS FIXING
def GetStream():
  req = urllib.request.Request("http://localhost:8080/rest/sitemaps/events/9f61d2f2-68bb-492b-b5d3-6a5d00c1a57f?sitemap=demo&pageid=FF_Bath", None, {"Accept": "text/event-stream"})
  try:
    with urllib.request.urlopen(req) as res:
      while True:
        res.readline()
        data = json.loads(res.readline()[6:-1].decode("utf-8"))
        res.readline()
        print(data["item"]["name"] + " " + data["item"]["state"])
  except urllib.error.HTTPError as err:
    return {"error":err.code}

  return {}

