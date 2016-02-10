import sys
print sys.argv
smiles_location = sys.argv[1]
destination_folder = sys.argv[2]

switchApp("T.E.S.T (Toxicity Estimation Software Tool)")
close_batch_button = exists("1444861040674.png")
if close_batch_button:
    click(close_batch_button)
    
click("1444850471970.png")
click("1444850488942.png")
type(smiles_location)
click("1444850546160.png")


click("1444850586082.png")
click("1444850597386.png")
text_field = find("1444851328866.png").left(100)
click(text_field)
type('a',KEY_CTRL)
type(destination_folder)
click("1444850700783.png")

endpoint_menu = find("1444851023626.png").right(100)
endpoint_list = endpoint_menu.above(50)

def close_result(): 
    #I would kill for function hoisting
    wait("1445639543422.png", 3600)
    type('w',KEY_CTRL)
    switchApp("T.E.S.T (Toxicity Estimation Software Tool)")
    click(endpoint_menu)

#fatheadminnow LC50
click(endpoint_menu)
wheel(endpoint_list, WHEEL_UP, 5)
fathead_button = find("1444860952236.png")
if fathead_button:
    click(fathead_button)
click("1444850761650.png")
close_result()

#menu items are 16 pixels separate
#Dap. magna lc50
click("1444853683124.png")
click("1444850761650.png")
close_result()

#T.pyrifo
click("1444853736895.png")
click("1444850761650.png")
close_result()

#oal rat ld50
click("1444853772273.png")
click("1444850761650.png")
close_result()

#bioaccum
click("1444853805690.png")
click("1444850761650.png")
close_result()

#developmental
click("1444853827216.png")
click("1444850761650.png")
close_result()

#mutagen
click("1444853855190.png")
click("1444850761650.png")
close_result()

#vapor presssure
wheel(endpoint_list, WHEEL_DOWN, 1)
click("1444854732672.png")
click("1444850761650.png")
close_result()

#water sol
wheel(endpoint_list, WHEEL_DOWN, 4)
click("1444854831199.png")        
click("1444850761650.png")
wait("1444853237918.png", 3600)
type('w',KEY_CTRL)