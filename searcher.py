import sys
import json
import pathlib
import parser
import copy

if len(sys.argv) < 2:
	print("A field to search in must be provided")
	sys.exit()
if len(sys.argv) < 3:
	print("A value to search for must be provided")
	sys.exit()
res = {"results": []}
log_dir = pathlib.Path("./logs/logs")
for path in log_dir.glob("log_*.json"):
	with open(path, "r") as f:
		for line in f:
			data = json.loads(line)
			if sys.argv[1] in ["auth_attempts"]:
				if len(sys.argv) < 4:
					print("A value to search for must be provided")
					sys.exit()
				if data["num_auth_attempts"] >= 1:
					for attempt in data["auth_attempts"]:
						if attempt[sys.argv[2]] == sys.argv[3]:
							res["results"].append(data)
			elif sys.argv[2] in ["auxiliary_data"]:
				if len(sys.argv) < 4:
					print("A value to search for must be provided")
					sys.exit()
				if data[sys.argv[1]][sys.argv[2]] == sys.argv[3]:
					res["results"].append(data)
			else:
				if data[sys.argv[1]] == sys.argv[2]:
					res["results"].append(data)

with open(f"searches/{sys.argv[1]}_{sys.argv[2]}_{sys.argv[3]}.json" if sys.argv[1] in ["auth_attempts", "auxiliary_data"] else f"searches/{sys.argv[1]}_{sys.argv[2]}.json", "w") as f:
	res["frequencies"] = None
	for entry in res["results"]:
		res["frequencies"] = parser.parse_dict(entry, res["frequencies"])
	del res["frequencies"]["last_timestamp"]
	res_copy = copy.deepcopy(res)
	for key1, val1 in res_copy["frequencies"].items():
		if not key1 == "auxiliary_data":
			res["frequencies"][key1] = dict(sorted(val1.items(), key=lambda x:x[1], reverse=True))
		else:
			for key2, val2 in val1.items():
				res["frequencies"][key1][key2] = dict(sorted(val2.items(), key=lambda x:x[1], reverse=True))
	json.dump(res, f)
