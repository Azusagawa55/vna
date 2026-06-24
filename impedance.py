def gamma_to_impedance(gamma, z0=50):
    z = z0 * (1 + gamma) / (1 - gamma)
    return {"real": z.real, "imag": z.imag}
