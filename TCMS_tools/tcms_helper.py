import sys
sys.path.append("C:/Users/user/Desktop/code/automation-test")
from constants import *
from TCMS_tools.tcms_fuctions import *
from tcms_api import TCMS

# TCMS setup
tcms_url = TCMS_URL
tcms_username = TCMS_USERNAME
tcms_password = TCMS_PASSWORD
rpc = TCMS(tcms_url, tcms_username, tcms_password).exec

methods = rpc.system.listMethods()
print("متدهای موجود روی سرور:")
for m in methods:
    print(m)
    help = rpc.system.methodHelp(str(m))
    print(help)
    


