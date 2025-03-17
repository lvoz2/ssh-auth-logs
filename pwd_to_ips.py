import sys
import json
import pathlib

if len(sys.argv) < 2:
	print("A password to search for must be provided")
	sys.exit()
ips = {}
log_dir = pathlib.Path("./logs/logs")
for path in log_dir.glob("log_*.json"):
	with open(path, "r") as f:
		for line in f:
			data = json.loads(line)
			if data["num_auth_attempts"] >= 1:
				for attempt in data["auth_attempts"]:
					if attempt["password"] == sys.argv[1]:
						if data["source_ip"] not in ips:
							ips[data["source_ip"]] = 0
						ips[data["source_ip"]] += 1

with open(f"{sys.argv[1]}_freq.json", "w") as f:
	json.dump(ips, f)
