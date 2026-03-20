import time
import mido

# Variables pour garder une trace des tempos et des temps entre les accords
last_chord_time = None
current_tempo_bpm = 120  # Tempo initial
last_bpm_values = []  # Liste des BPM pour une moyenne mobile
min_interval = 0.2  # Seuil minimum entre les accords
lissage_factor = 0.1  # Facteur de lissage pour le tempo
canal_cible = 4  # Canal MIDI spécifique à filtrer (par exemple, canal 4)

# Fonction pour calculer le BPM en fonction de l'intervalle
def calculer_bpm(interval):
    bpm_calculé = 60 / interval
    last_bpm_values.append(bpm_calculé)
    
    # Garder un nombre fixe de valeurs de BPM pour la moyenne mobile
    if len(last_bpm_values) > 4:
        last_bpm_values.pop(0)
    
    # Calculer le BPM moyen
    bpm_moyenne = sum(last_bpm_values) / len(last_bpm_values)
    return bpm_moyenne

# Fonction pour envoyer le tempo au clavier via un message SysEx
def send_tempo_to_keyboard(tempo_bpm):
    # Convertir le tempo en microsecondes par noire
    tempo_microseconds = int(60000000 / tempo_bpm)
    
    # Afficher la valeur du tempo en microsecondes
    print(f"Tempo en microsecondes : {tempo_microseconds}")
    
    # Diviser tempo_microseconds en 4 octets 7 bits (chaque octet doit être dans la plage 0-127)
    tempo_bytes = [
        (tempo_microseconds >> 24) & 0x7F,  # 1er octet (bits 24-31)
        (tempo_microseconds >> 16) & 0x7F,  # 2e octet (bits 17-23)
        (tempo_microseconds >> 8) & 0x7F,   # 3e octet (bits 10-16)
        tempo_microseconds & 0x7F           # 4e octet (bits 3-9)
    ]
    
    # Affichage des octets de tempo pour débogage
    print(f"Octets du tempo (avant envoi) : {tempo_bytes}")
    
    # Vérifier que chaque octet est bien dans la plage 0-127 avant l'envoi
    for byte in tempo_bytes:
        if byte < 0 or byte > 127:
            print(f"Erreur : octet hors plage : {byte}")
            return
    
    # Construire le message SysEx avec les octets de tempo
    tempo_message_data = [0xF0, 0x7F, 0x7F, 0x06, 0x01, 0x00] + tempo_bytes + [0xF7]
    
    # Affichage des données du message avant l'envoi pour débogage
    print("Données du message SysEx : ", tempo_message_data)

    #Vérification des octets du message SysEx pour s'assurer qu'ils sont dans la plage 0-127
    for byte in tempo_message_data[1:-1]:
        if not (0 <= byte <= 127):
            print(f"Erreur : un octet hors de la plage 0-127 : {byte}")
            break
        else:
            print("Données du message SysEx :", tempo_message_data)
        
    # Envoi du message SysEx
    try:
        tempo_message = mido.Message('sysex', data=tempo_message_data)
        midi_out.send(tempo_message)  # Envoi du message SysEx
        print(f"Tempo envoyé: {tempo_bpm} BPM")
    except ValueError as e:
        print(f"Erreur lors de l'envoi du message SysEx : {e}")

# Fonction de traitement des messages MIDI
def traiter_messages_midi(msg):
    global last_chord_time, current_tempo_bpm

    # Vérifier si le message contient l'attribut 'channel' (utile pour 'note_on', 'note_off', etc.)
    if not hasattr(msg, 'channel'):
        return  # Ignorer les messages qui n'ont pas de canal (par exemple, sysex)

    # Filtrer les messages en fonction du canal MIDI
    if msg.channel != canal_cible:  # Ignorer les messages d'autres canaux
        return

    if msg.type == 'note_on':
        chord_pressed_time = time.perf_counter()
        
        if last_chord_time is not None:
            interval = chord_pressed_time - last_chord_time
            if interval > min_interval:  # S'assurer que l'intervalle est assez grand
                bpm_calculé = calculer_bpm(interval)
                
                # Lissage du tempo
                current_tempo_bpm = current_tempo_bpm * (1 - lissage_factor) + bpm_calculé * lissage_factor
        
        last_chord_time = chord_pressed_time  # Mettre à jour le temps de la dernière note_on

# Initialisation des ports MIDI
ports_in = mido.get_input_names()
ports_out = mido.get_output_names()

# Choisir un port MIDI IN et MIDI OUT
port_in_index = 2  # Change selon ton clavier
port_out_index = 4  # Change selon ton port MIDI de sortie

midi_in = mido.open_input(ports_in[port_in_index])
midi_out = mido.open_output(ports_out[port_out_index])

# Afficher les ports MIDI disponibles pour vérifier
print("Ports MIDI IN disponibles :")
for i, port in enumerate(ports_in):
    print(f"{i}: {port}")
    
print("\nPorts MIDI OUT disponibles :")
for i, port in enumerate(ports_out):
    print(f"{i}: {port}")

# Lancer la fonction de traitement des messages MIDI
while True:
    for msg in midi_in.iter_pending():  # Lire les messages MIDI entrants
        print(f"Message MIDI reçu : {msg}")
        traiter_messages_midi(msg)
        
        # Envoyer le tempo mis à jour au clavier
        send_tempo_to_keyboard(current_tempo_bpm)
        
        # Afficher le tempo calculé
        print(f"Tempo actuel : {current_tempo_bpm:.2f} BPM")

    time.sleep(0.05)  # Attendre un peu pour ne pas surcharger la CPU
