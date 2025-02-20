"""This script is used to obtain username/userid for running tests against server
"""
import json
import os

from modelon.impact.client import Client

thisdir = os.path.dirname(__file__)
userid_file_name = thisdir + "/userid.json"

print(f"Generating {userid_file_name}")
try:
    with open(userid_file_name, "w", encoding="utf-8") as userid_file:
        print("Requesting user info from server")
        me = Client().get_me()
        userid = {"username": me.username, "id": me.id, "tenantId": me.tenant.id}
        json.dump(userid, userid_file)
except Exception as e:
    print(f"Request failed {str(e)}; removing the file.")
    os.remove(userid_file_name)
