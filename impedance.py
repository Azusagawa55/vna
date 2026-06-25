import numpy as np


def gamma_to_impedance(gamma, z0=50):
    z = z0 * (1 + gamma) / (1 - gamma)
    return {"real": z.real, "imag": z.imag}


class ImpedanceMatching:

    def __init__(self, z0=50):
        self.z0 = z0

    def gamma_to_impedance(self, real, imag):

        gamma = complex(real, imag)

        z = self.z0 * (1 + gamma) / (1 - gamma)

        return z

    def calculate_l_network(
            self,
            real,
            imag,
            frequency):

        z = complex(real, imag)

        R = z.real
        X = z.imag

        omega = 2 * np.pi * frequency

        if R <= 0:
            return {
                "error":
                    "Invalid impedance"
            }

        if R < self.z0:

            Q = np.sqrt((self.z0 / R) - 1)

            Xseries = Q * R
            Xparallel = self.z0 / Q

        else:

            Q = np.sqrt((R / self.z0) - 1)

            Xseries = self.z0 * Q
            Xparallel = R / Q

        results = {}

        results["Q"] = float(Q)

        if Xseries > 0:

            Ls = Xseries / omega

            results["Series Component"] = "Inductor"
            results["Series Value"] = f"{Ls * 1e9:.3f} nH"

        else:

            Cs = 1 / (omega * abs(Xseries))

            results["Series Component"] = "Capacitor"
            results["Series Value"] = f"{Cs * 1e12:.3f} pF"

        if Xparallel > 0:

            Lp = Xparallel / omega

            results["Parallel Component"] = "Inductor"
            results["Parallel Value"] = f"{Lp * 1e9:.3f} nH"

        else:

            Cp = 1 / (omega * abs(Xparallel))

            results["Parallel Component"] = "Capacitor"
            results["Parallel Value"] = f"{Cp * 1e12:.3f} pF"

        return results
