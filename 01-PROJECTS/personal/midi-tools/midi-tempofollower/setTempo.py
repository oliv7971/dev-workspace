import mido
import time

# Lister les ports de sortie disponibles
ports = mido.get_output_names()
print("Ports de sortie disponibles :")
for i, port in enumerate(ports):
    print(f"{i}: {port}")

# Choisir un port spécifique
port_index = 4  # Change l'index si nécessaire pour ton clavier
midi_out = mido.open_output(ports[port_index])

# Fonction pour envoyer MIDI Clock avec meilleure précision
def send_midi_clock(tempo_bpm):
    # Calculer la fréquence de MIDI Clock en fonction du tempo
    ticks_per_second = tempo_bpm * 24 / 60  # Nombre de ticks par seconde
    seconds_per_tick = 1 / ticks_per_second  # Temps entre chaque tick
    
    print(f"Tempo à {tempo_bpm} BPM, avec {ticks_per_second} ticks par seconde.")

    # Initialiser le temps de la première boucle
    start_time = time.perf_counter()
    
    while True:
        # Envoi du message MIDI Clock
        midi_out.send(mido.Message('clock'))
        
        # Mesurer le temps écoulé
        elapsed_time = time.perf_counter() - start_time
        
        # Attendre jusqu'à ce que l'intervalle de temps soit respecté
        time_to_wait = seconds_per_tick - elapsed_time % seconds_per_tick
        time.sleep(time_to_wait)

# Exemple de changement de tempo à 120 BPM
try:
    send_midi_clock(120)  # Change le tempo à 120 BPM
except KeyboardInterrupt:
    print("Arrêté par l'utilisateur.")

# Fermer le port MIDI
midi_out.close()
