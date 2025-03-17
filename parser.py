#!/usr/bin/python

import datetime
import json
import sys

import ssh_log_combiner as ssh_parser

def parse_dict(data, res = None):
    if res is None:
        res = {"last_timestamp": "2024-01-01 01:00:00.000000", "durations": {}, "ips": {}, "usernames": {}, "passwords": {}, "usr:pwd": {}, "auxiliary_data": {"client_version": {}, "recv_cipher": {}, "recv_mac": {}, "recv_compression": {}}}
    if data["protocol"] == "ssh":
        if data["source_ip"] not in res["ips"]:
            res["ips"][data["source_ip"]] = 0
        res["ips"][data["source_ip"]] += 1
        if data["duration"] not in res["durations"]:
        	res["durations"][data["duration"]] = 0
        res["durations"][data["duration"]] += 1
        if data["num_auth_attempts"] > 0:
            for i in range(len(data["auth_attempts"])):
                if data["auth_attempts"][i]["username"] not in res["usernames"]:
                    res["usernames"][data["auth_attempts"][i]["username"]] = 0
                res["usernames"][data["auth_attempts"][i]["username"]] += 1
                if data["auth_attempts"][i]["password"] not in res["passwords"]:
                    res["passwords"][data["auth_attempts"][i]["password"]] = 0
                res["passwords"][data["auth_attempts"][i]["password"]] += 1
                if f'{data["auth_attempts"][i]["username"]}:{data["auth_attempts"][i]["password"]}' not in res["usr:pwd"]:
                	res["usr:pwd"][f'{data["auth_attempts"][i]["username"]}:{data["auth_attempts"][i]["password"]}'] = 0
                res["usr:pwd"][f'{data["auth_attempts"][i]["username"]}:{data["auth_attempts"][i]["password"]}'] += 1
        if data["auxiliary_data"]["client_version"] not in res["auxiliary_data"]["client_version"]:
            res["auxiliary_data"]["client_version"][data["auxiliary_data"]["client_version"]] = 0
        res["auxiliary_data"]["client_version"][data["auxiliary_data"]["client_version"]] += 1
        if data["auxiliary_data"]["recv_cipher"] not in res["auxiliary_data"]["recv_cipher"]:
            res["auxiliary_data"]["recv_cipher"][data["auxiliary_data"]["recv_cipher"]] = 0
        res["auxiliary_data"]["recv_cipher"][data["auxiliary_data"]["recv_cipher"]] += 1
        if data["auxiliary_data"]["recv_mac"] not in res["auxiliary_data"]["recv_mac"]:
            res["auxiliary_data"]["recv_mac"][data["auxiliary_data"]["recv_mac"]] = 0
        res["auxiliary_data"]["recv_mac"][data["auxiliary_data"]["recv_mac"]] += 1
        if data["auxiliary_data"]["recv_compression"] not in res["auxiliary_data"]["recv_compression"]:
            res["auxiliary_data"]["recv_compression"][data["auxiliary_data"]["recv_compression"]] = 0
        res["auxiliary_data"]["recv_compression"][data["auxiliary_data"]["recv_compression"]] += 1
    else:
        print("Non-ssh request found")
    return res

def parse_file(file_path: str, old_data: dict[str, str | dict[str, int | dict[str, int]]]) -> dict[str, str | dict[str, int | dict[str, int]]]:
    if old_data == {} or "ips" not in old_data or "usernames" not in old_data or "passwords" not in old_data or "auxiliary_data" not in old_data:
        freq = {"last_timestamp": "2024-01-01 01:00:00.000000", "durations": {}, "ips": {}, "usernames": {}, "passwords": {}, "usr:pwd": {}, "auxiliary_data": {"client_version": {}, "recv_cipher": {}, "recv_mac": {}, "recv_compression": {}}}
    else:
        freq = old_data
    found_newer = False
    with open(file_path, "r") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            if found_newer or datetime.datetime.fromisoformat(freq["last_timestamp"]) < datetime.datetime.fromisoformat(data["timestamp"]):
                try:
                    freq = parse_dict(data, freq)
                    freq["last_timestamp"] = data["timestamp"]
                    found_newer = True
                except Error as e:
                    print(file_path)
                    raise e
    return freq

if __name__ == "__main__":
    session_data = []
    days = set()
    with open("logs/log_session.json", "r") as f:
    	for line in f:
    		session_data.append(line)
    for i, line in enumerate(session_data):
        try:
    	    log = json.loads(line)
        except Exception as e:
            print("JSON Load Error at", i + 1, "content", line)
            raise e
        day = datetime.datetime.fromisoformat(log["timestamp"])
        days.add(day.date())
        with open(day.strftime("logs/logs/log_%Y_%m_%d.json"), "a") as f:
            f.write(line)
    with open("logs/log_session.json", "w") as f:
        f.write("")
    for day in days:
	    data = {"last_timestamp": "2024-01-01 01:00:00.000000"}
	    try:
	        with open(day.strftime("logs/summaries/ssh_log_%Y_%m_%d.json"), "r") as f:
	            data = parse_file(day.strftime("logs/logs/log_%Y_%m_%d.json"), json.load(f))
	    except FileNotFoundError as e:
	        data = parse_file(day.strftime("logs/logs/log_%Y_%m_%d.json"), data)
	    with open(day.strftime("logs/summaries/ssh_log_%Y_%m_%d.json"), "w") as f:
	        json.dump(data, f)
    ssh_parser.run()
