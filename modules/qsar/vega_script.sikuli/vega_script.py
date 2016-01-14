import sys
print sys.argv

smiles_location = sys.argv[1]
output_folder = sys.argv[2]

switchApp("VEGA in silico")
if exists("1444947945179.png"):
    click("1444947945179.png")
click(Pattern("1444946567087.png").similar(0.80))
click("1444946370789.png")
wait("1444947035647.png", 3600)
type(Key.DELETE)
type(smiles_location)
click("1444850546160.png")
wait("1444946506227.png", 3600)
type(Key.ENTER)
click("1444947921977.png")

def select_all_models():
    if exists(Pattern("1444947726351.png").similar(0.90)):
        button = find(Pattern("1444947769086.png").targetOffset(-50,0))
        click(button)


tox_unselected = exists("1444947140734.png")
if tox_unselected:
    click(tox_unselected)

select_all_models()
click("1444947994210.png")
select_all_models()
click("1444948010416.png")
select_all_models()
click("1444948036334.png")
select_all_models()

click("1444948536113.png")
if exists(Pattern("1444948690707.png").similar(0.97)):
    click(Pattern("1444948690707.png").similar(0.95))


click(Pattern("1445285424478.png").targetOffset(-31,40))
type('a',KEY_CTRL)
type(Key.DELETE)
type(output_folder) 
    
if exists(Pattern("1444948603633.png").similar(0.95).targetOffset(-32,0)):
    click(Pattern("1444948603633.png").similar(0.95).targetOffset(-32,0))

click(Pattern("1445285465887.png").targetOffset(-5,41))
type('a',KEY_CTRL)
type(Key.DELETE)
type(output_folder)
            
click("1444949136593.png")

wait("1445284676452.png", 3600)
click("1445284703964.png")

            