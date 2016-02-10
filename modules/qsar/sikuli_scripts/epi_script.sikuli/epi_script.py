import sys
import datetime
import os

try:
    smiles_location = sys.argv[1]
    destination_folder = sys.argv[2]
    log_file = sys.argv[3]
except:
    smiles_location = r"C:\inetpub\wwwroot\clicc-flask\modules\qsar\smiles.txt"
    destination_folder = r"C:\inetpub\wwwroot\clicc-flask\modules\qsar\results"
    log_file = r"C:\inetpub\wwwroot\clicc-flask\modules\qsar\logging\logging.txt"

if log_file:
    try: 
       log = open(log_file, 'a')
       log.write("Started Epi Script. Log Loaded\n")
    except:
       log = False

App.focus("EPI Suite")
click("1454457927406.png")
click("1454458022016.png")
wait(Pattern("1454109316523.png").similar(0.80),10)
click(Pattern("1454109316523.png").similar(0.80).targetOffset(0,-6))
wait(Pattern("1445283522889.png").targetOffset(70,0), 10)
type(Pattern("1445283522889.png").targetOffset(70,0), smiles_location)
click("1444335871023.png")
click("1444335889514.png")
click("1444335910641.png")
wait(Pattern("1444335926995.png").similar(0.80), 3600)
click("1444335939011.png")
wait("1445288333209.png", 3600)
click("1444335954211.png")
wait("1445288120483.png", 3600)
type(destination_folder + r"\EPI_results.txt")
click("1445288153400.png")
if log:
    log.write("script reached end.\n\n")
    log.close()