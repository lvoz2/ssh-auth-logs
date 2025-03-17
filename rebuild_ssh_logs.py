import json
import pathlib
#import datetime

import parser

def run():
	log_dir = pathlib.Path("logs/logs")
	for path in log_dir.glob("log_*.json"):
		if path.name == "log_session.json":
			continue
		res = None
		with open(path, "r") as f:
			for i, line in enumerate(f):
				data = json.loads(line)
				try:
					res = parser.parse_dict(data, res)
				except KeyError as e:
					print(f"{i} {path}")
					raise e
		with open(f"rebuilt/ssh_{path.name}", "w") as f:
			json.dump(res, f)

if __name__ == "__main__":
	run()
