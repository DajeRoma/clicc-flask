from ft.fate_and_transport import FateAndTransport
from exposure.exposure import Exposure

if __name__ == "__main__":
    env_sheet = "SF_glycerin_beta.xlsx"
    chem_sheet = "SF_glycerin_beta.xlsx"

    f = FateAndTransport()
    e = Exposure()

    f.load_chem(chem_sheet)
    f.load_environment(env_sheet)
    f_out = f.run()
    f.write_output(f_out)

    e_out = e.run(f_out)
    e.write_output(e_out)
