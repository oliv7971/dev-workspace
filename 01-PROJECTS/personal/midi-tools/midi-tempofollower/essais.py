def send_tempo_to_keyboard(tempo_bpm):
    # Convertir le tempo en microsecondes par noire
    tempo_microseconds = int(60000000 / tempo_bpm)
    
    # S'assurer que les valeurs des octets sont dans la plage correcte (0-127)
    tempo_bytes = [
        (tempo_microseconds >> 24) & 0x7F,  # Premier octet de la valeur du tempo
        (tempo_microseconds >> 16) & 0x7F,
        (tempo_microseconds >> 8) & 0x7F,
        tempo_microseconds & 0x7F  # Dernier octet de la valeur du tempo
    ]
    
    # Vérifier si tous les octets sont dans la plage 0-127
    for byte in tempo_bytes:
        if not (0 <= byte <= 127):
            print(f"Erreur : octet hors plage : {byte}")
            return
    
    # Créer le message SysEx
    tempo_message = mido.Message('sysex', data=[0xF0, 0x7F, 0x7F, 0x06, 0x01, 0x00, tempo_bpm & 0x7F, (tempo_bpm >> 7) & 0x7F, 0xF7])
    
    # Afficher les données avant l'envoi du message
    print("Données du message tempo_message avant envoi :")
    print("Données brutes du tempo (en octets) :", tempo_message.data)
    print(f"Tempo (BPM calculé) : {tempo_bpm:.2f}")
    print("Message SysEx complet (avec préfixe et suffixe) :")
    print([0xF0, 0x7F, 0x7F, 0x06, 0x01, 0x00, tempo_bpm & 0x7F, (tempo_bpm >> 7) & 0x7F, 0xF7])
    
    # Affiche le message complet avant l'envoi
    print(f"Message complet SysEx : {tempo_message}")
    
    # Envoi du message
    midi_out.send(tempo_message)
