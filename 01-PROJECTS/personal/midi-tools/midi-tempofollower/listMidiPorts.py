import rtmidi

# Créer une instance de MidiOut
midi_out = rtmidi.MidiOut()

# Liste des périphériques MIDI disponibles
available_ports = midi_out.get_ports()

# Afficher les ports disponibles
if available_ports:
    print("Ports MIDI disponibles :")
    for i, port in enumerate(available_ports):
        print(f"{i}: {port}")
else:
    print("Aucun périphérique MIDI disponible.")
    
# Fermer la connexion
midi_out.close_port()
