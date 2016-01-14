import sys
print sys.argv
smiles_location = sys.argv[1]
destination_folder = sys.argv[2]


switchApp("EPI Suite")
click("1444335166809.png")
click("1444335203652.png")
wait("1444335236072.png", 20)
click("1444335236072.png")
wait(Pattern("1445283522889.png").targetOffset(70,0), 20)
type(Pattern("1445283522889.png").targetOffset(70,0), smiles_location)
click("1444335871023.png")
click("1444335889514.png")
click("1444335910641.png")
wait(Pattern("1444335926995.png").similar(0.80), 3600)
click("1444335939011.png")
wait("1445288333209.png", 3600)
click("1444335954211.png")
wait("1445288120483.png", 3600)
type(destination_folder + "\\EPI_results.txt")
click("1445288153400.png")
