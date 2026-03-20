def kappa_zenith_correction(temp, press, humid):
    """
    Modèle de Kappa-Zenith pour calculer la correction en ppm.
    temp : température en degrés Celsius
    press : pression en hPa
    humid : humidité relative en pourcentage
    """
    A = 0.1  # Exemple de coefficient empirique
    B = 0.2  # Exemple de coefficient empirique

    correction = A * (press / temp) + B * humid
    return correction


def hopfield_correction(temp, press, humid):
    """
    Modèle de Hopfield pour calculer la correction en ppm.
    temp : température en degrés Celsius
    press : pression en hPa
    humid : humidité relative en pourcentage
    """
    A = 0.3  # Exemple de coefficient empirique
    B = 0.4  # Exemple de coefficient empirique

    correction = A * (press / temp) + B * humid
    return correction


def saastamoinen_correction(temp, press, humid):
    """
    Modèle de Saastamoinen pour calculer la correction en ppm.
    temp : température en degrés Celsius
    press : pression en hPa
    humid : humidité relative en pourcentage
    """
    correction = 0.002277 * (press / (temp + 273.15)) + 0.0025 * (1 + 0.0026 * humid) / (1 - 0.0026 * humid)
    return correction

def leica_correction(temp, press, humid):
    """
    La formule ci-dessous est valable pour les appareils de type LEICA utilisant une onde porteuse de 0.85µ.
    temp : température en degrés Celsius
    press : pression en hPa
    humid : humidité relative en pourcentage
    A= 1/273.16
    X= 7.5xT/(237.3+T)+0.7857
    Correction en ppm = 281.8 - ((0.29065 x P) / (1+A x T) - (4.126 x10E-4 x H) / (1+A xT ) x 10^X))
    """

    a = 1 / 273.16
    x = 7.5 * temp / (237.3 + temp) + 0.7857

    correction = 281.8 - ((0.29065 * press) / (1 + a * temp) - (4.126 * 0.0001 * humid) / (1 + a * temp) * 10**x)
    return correction


# Exemple d'utilisation des fonctions
temp = 4.6  # Température en Celsius
press = 1005  # Pression en hPa
humid = 97  # Humidité relative en pourcentage

correction_kappa_zenith = kappa_zenith_correction(temp, press, humid)
correction_hopfield = hopfield_correction(temp, press, humid)
correction_saastamoinen = saastamoinen_correction(temp, press, humid)
correction_leica = leica_correction(temp, press, humid)

print("Correction selon le modèle de Kappa-Zenith :", correction_kappa_zenith, "ppm")
print("Correction selon le modèle de Hopfield :", correction_hopfield, "ppm")
print("Correction selon le modèle de Saastamoinen :", correction_saastamoinen, "ppm")
print("Correction selon le modèle de Leica :", correction_leica, "ppm")
