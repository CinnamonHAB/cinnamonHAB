import urllib.request
import json
import ff_com

addr = "http://127.0.0.1:8080" # updated with SedAddr()
rest_path = "/rest"
items_path = rest_path + "/items"
subscription_path = rest_path + "/sitemaps/events/subscribe"
stream_url = "" # updated after Subscribe()
map_item_states_to_target_states = {} # update in _GetTargetState

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
def _GetItemNamesAndTypesDict(item):
  items = {}
  if item["type"] != "Group":
    items[item["name"]] = item["type"]
  else:
    for v in item["members"]:
      items.update(_GetItemNamesAndTypesDict(v))

  return items

# Gets a problem text for the specified group and the target state.
# Target state will be copied as given to the problem text.
def GetProblem(group_name, target_state):
  global map_item_states_to_target_states
  group = GetItem(group_name)
  if ("error" in group):
    return "error " + str(group["error"])
  items = _GetItemNamesAndTypesDict(group)
  for item in map_item_states_to_target_states:
    items.pop(item)
  items.update({key.replace("s","l") : "Lamp" for key in items})
  item_names = [key for key in items]
  item_types_names = ["(" + items[key] + " " + key + ")" for key in items]
  item_names_group = ["(IN " + key + " " + group_name + ")" for key in items]
  item_states = ["(not (ON " + key + "))" if GetItem(key.replace("l", "s"))["state"] == "OFF" else "(ON " + key + ")" for key in items if key[0] == "l"]
  problem = "(define\n(problem problem-name)\n(:domain cinnemain)\n"
  problem += "(:objects " + " ".join(item_names) + " " + group_name + ")\n"
  problem += "(:init " + "\n".join(item_types_names) + "\n"
  problem += "(GROUP " + group_name + ")\n"
  problem += "\n".join(item_names_group) + "\n"
  problem += "\n".join(item_states) + "\n"
  problem += "\n".join(["(AFFECTS " + item + " " + item.replace("s", "l") + ")" for item in items if item[0] == "s"]) + ")\n"
  problem += target_state + ")\n"
  return problem

# Just a wrapper for file printing. In this case used to print problem files.
def WriteProblem(problem):
  with open("problem.txt", "w") as problem_file:
    print(problem, file=problem_file)

# Subscribes to events from OpenHab. To actually get the stream, GetStream() needs to be called.
# Updates stream_url. If all goes well returns {}.
# If something goes wrong, returns {"error":400} (but using the real code that it got).
def Subscribe():
  global addr
  global subscription_path
  global stream_url
  req = urllib.request.Request(addr+subscription_path, None, {"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
  try:
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    stream_url = res["context"]["headers"]["Location"][0]
  except urllib.error.HTTPError as err:
    return {"error":err.code}
  return {}

# Loads target states from target_states.json.
# Returns a trget state string, depending on the given item and its new state.
def _GetTargetState(item, state):
  global map_item_states_to_target_states
  with open("target_states.json", "r") as file:
    map_item_states_to_target_states = json.loads(file.read())
  try:
    target_item_states = map_item_states_to_target_states[item][state]
  except Exception as e:
    return None
  target_state = ["(ON " + item + ")" if target_item_states[item] else "(not (ON " + item + "))" for item in target_item_states]
  return "(:goal (and\n" + "\n".join(target_state) + "))\n"

# Extract steps from metric ff's output.
# Returns {"item1":"state1", "item2":"state2", "item3":"state3"}.
def _GetSteps(ff_output):
  ff_output = ff_output.lower()
  is_steps = False
  steps_str = []
  for line in ff_output.splitlines():
    if line.startswith("step"):
      try:
        steps_str.append(line.split(":")[1].strip())
      except Exception as e:
        return {}
      is_steps = True
    elif is_steps and line == "":
      break
    elif is_steps:
      steps_str.append(line.split(":")[1].strip())
  steps = {}
  for step in steps_str:
    item = step.split(" ")[1]
    action = step.split(" ")[0]
    if action.startswith("toggle"):
      if GetItem(item)["state"] == "OFF":
        steps[item] = "ON"
      else:
        steps[item] = "OFF"
  return steps

# Opens a long-pollin stream for the desired sitemap and pageid (can be found out through browser).
# Must be called after Subscribe(). Once called, the connection will not close and will be kept open.
# If something goes wrong, returns {"error":400} (but using the real code that it got).
def StartStream(sitemap, pageid):
  global stream_url
  req = urllib.request.Request(stream_url + "?sitemap=" + sitemap + "&pageid=" + pageid, None, {"Accept": "text/event-stream"})
  try:
    with urllib.request.urlopen(req) as res:
      while True:
        res.readline()
        data = json.loads(res.readline()[6:-1].decode("utf-8"))
        res.readline()
        item = data["item"]["name"]
        state = data["item"]["state"]
        print(item + " changed to " + state)
        target_state = _GetTargetState(item, state)
        print(target_state)
        if target_state != None:
          problem = GetProblem("g", target_state)
          WriteProblem(problem)
          ff_output = ff_com.get_plan("./", "domain.txt", "problem.txt", "0")
          steps = _GetSteps(ff_output)
          for item in steps:
            SetItem(item, steps[item])
  except urllib.error.HTTPError as err:
    return {"error":err.code}
  return {}

