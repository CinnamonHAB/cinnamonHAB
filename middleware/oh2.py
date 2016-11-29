import urllib.request
import json
import ff_com

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
  items.pop("action")
  items.update({key.replace("s","l"): items[key] for key in items})
  items.update({key: "Lamp" for key in items if key[0] == "l"})
  item_names = [key for key in items]
  item_types_names = ["(" + items[key] + " " + key + ")" for key in items]
  item_names_group = ["(IN " + key + " " + group_name + ")" for key in items]
  item_states = [("(not " if GetItem(key.replace("l", "s"))["state"] == "OFF" else " " ) + "(ON " + key + ")" + (") " if GetItem(key.replace("l", "s"))["state"] == "OFF" else " ") for key in items if key[0] == "l"]
  problem = "(define\n(problem problem-name)\n(:domain cinnemain)\n"
  problem += "(:objects " + " ".join(item_names) + " " + group_name + ")\n"
  problem += "(:init " + "\n".join(item_types_names) + "\n"
  problem += "(GROUP " + group_name + ")\n"
  problem += "\n".join(item_names_group) + "\n"
  problem += "\n".join(item_states) + "\n"
  problem += "(AFFECTS s1 l1)\n"
  problem += "(AFFECTS s2 l2)\n"
  problem += "(AFFECTS s3 l3))\n"
  problem += target_state + "))"
  return problem

# Just a wrapper for file printing. In this case used to print problem files.
def WriteProblem(problem):
  with open("problem.txt", "w") as problem_file:
    print(problem, file=problem_file)











subscription_url = ""

def Subscribe():
  global subscription_url
  req = urllib.request.Request("http://localhost:8080/rest/sitemaps/events/subscribe", None, {"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
  try:
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    subscription_url = res["context"]["headers"]["Location"][0]
  except urllib.error.HTTPError as err:
    return {"error":err.code}

  return {}


# VERY UGLY!!!
# TODO: LSTRZ
# NEEDS FIXING
def GetStream(sitemap, pageid):
  req = urllib.request.Request(subscription_url + "?sitemap=" + sitemap + "&pageid=" + pageid, None, {"Accept": "text/event-stream"})
  try:
    with urllib.request.urlopen(req) as res:
      while True:
        res.readline()
        data = json.loads(res.readline()[6:-1].decode("utf-8"))
        res.readline()
        item = data["item"]["name"]
        state = data["item"]["state"]
        print(item + " changed to " + state)
        if item == "action":
          if state == "ON":
            target_state = "(:goal (and (ON l1) (ON l2) (ON l3) )"
          elif state == "OFF":
            target_state = "(:goal (and (not (ON l1)) (not (ON l2)) (not (ON l3)) )"

          problem = GetProblem("g", target_state)
          WriteProblem(problem)
          print(ff_com.get_plan("./", "domain.txt", "problem.txt", "0"))
  except urllib.error.HTTPError as err:
    return {"error":err.code}

  return {}

