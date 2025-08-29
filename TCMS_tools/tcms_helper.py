from constants import *
from functions import *
from TCMS_tools.tcms_fuctions import *
from tcms_api import TCMS
import TCMS_tools.tcms_maps as tcms_maps

# TCMS setup
tcms_url = TCMS_URL
tcms_username = TCMS_USERNAME
tcms_password = TCMS_PASSWORD
rpc = TCMS(tcms_url, tcms_username, tcms_password).exec

methods = rpc.system.listMethods()
print("متدهای موجود روی سرور:")
for m in methods:
    print(m)

help = rpc.system.methodHelp("TestExecution.add_comment")
print(help)

