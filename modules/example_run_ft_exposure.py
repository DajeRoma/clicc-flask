from ft.fate_and_transport import FateAndTransport
from exposure.exposure import Exposure

if __name__ == "__main__":
    # put these in the same folder as this script or provide a path
    env_sheet = "SF_glycerin_beta.xlsx"
    chem_sheet = "SF_glycerin_beta.xlsx"

    # to include QSAR, chem sheet would be replaced with the output
    # of the QSAR module and QSAR would either be given a SMILES argument to it
    # "run" method, or run would be given no arguments and it would use whatever
    # SMILES were included in smiles.txt

    f = FateAndTransport()
    e = Exposure()

    f.load_chem(chem_sheet)
    f.load_environment(env_sheet)
    f_out = f.run()
    f.write_output(f_out)

    e_out = e.run(f_out)
    e.write_output(e_out)
