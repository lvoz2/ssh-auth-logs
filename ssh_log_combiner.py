#!/usr/bin/python

import pathlib
import copy
import json
import sys

def run():
	log_dir = pathlib.Path("./frequency_tables")
	data = {}
	for file in log_dir.iterdir():
		if file.name[:7] == "ssh_log":
			with file.open("r") as f:
				log_data: dict[str, str | dict[str, int | dict[str, int]]] = json.load(f)
				if data == {}:
					data = log_data
					del data["last_timestamp"]
				else:
					for key1, val1 in log_data.items():
						if not isinstance(val1, str):
							for key2, val2 in val1.items():
								if not key1 == "auxiliary_data":
									if key2 not in data[key1]:
										data[key1][key2] = 0
									data[key1][key2] += val2
								else:
									for key3, val3 in val2.items():
										if key3 not in data[key1][key2]:
											data[key1][key2][key3] = 0
										data[key1][key2][key3] += val3
	data_copy = copy.deepcopy(data)
	for key1, val1 in data_copy.items():
		if not key1 == "auxiliary_data":
			data[key1] = dict(sorted(val1.items(), key=lambda x:x[1], reverse=True))
		else:
			for key2, val2 in val1.items():
				data[key1][key2] = dict(sorted(val2.items(), key=lambda x:x[1], reverse=True))
	with open("ssh_log.json", "w") as f:
		json.dump(data, f)


if __name__ == "__main__":
	print(sys.argv)
	try:
		run()
	except Exception as e:
		raise e
