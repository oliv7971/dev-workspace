import mido

# Lister les ports de sortie et entrée disponibles
ports_in = mido.get_input_names()
ports_out = mido.get_output_names()

print("Ports MIDI IN disponibles :")
for i, port in enumerate(ports_in):
    print(f"{i}: {port}")

print("\nPorts MIDI OUT disponibles :")
for i, port in enumerate(ports_out):
    print(f"{i}: {port}")

# Choisir un port MIDI IN et MIDI OUT
port_in_index = 2  # Change selon ton clavier
port_out_index = 4  # Change selon ton port MIDI de sortie

# Ouvrir les ports MIDI
midi_in = mido.open_input(ports_in[port_in_index])
midi_out = mido.open_output(ports_out[port_out_index])

# Fonction pour tester la réception des messages MIDI
def test_midi_input():
    print("En attente de messages MIDI...")
    while True:
        for msg in midi_in.iter_pending():  # Lire les messages MIDI entrants
            print(f"Message reçu : {msg}")  # Affiche chaque message reçu

# Lancer la fonction de test
try:
    test_midi_input()
except KeyboardInterrupt:
    print("Arrêté par l'utilisateur.")

# Fermer les ports MIDI
midi_in.close()
midi_out.close()
