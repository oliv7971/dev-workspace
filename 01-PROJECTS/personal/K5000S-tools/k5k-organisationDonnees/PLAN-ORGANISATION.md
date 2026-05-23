# Plan d'organisation des données Kawai K5000S

## Analyse de l'existant

**Emplacement actuel :** `D:\01-MUSIQUE\03-KAWAI`  
**Taille totale estimée :** ~4 Go (dont ~1.5 Go de samples KSF, ~855 Mo de RAR, ~844 Mo d'EXE, ~235 Mo de PDF, ~211 Mo de ZIP)  
**Nombre de fichiers :** ~10 000+

### Problèmes identifiés

1. **Doublons massifs de documentation PDF** - Le même PDF existe en 3-5 copies :
   - `Kawai_K5000S_Manual.pdf` → dans `01-KAWAI`, `KAWAI`, `04-KAWAI DISKS`
   - `kawai_k5000_wizoo_1_of_2.pdf` → dans `01-DOCUMENTATION KAWAI`, `03-KAWAI`, `04-KAWAI DISKS`, `KAWAI`
   - `Kawai_K5000_ServiceManual.pdf` → dans `01-KAWAI`, `01-DOCUMENTATION KAWAI`, `KAWAI`, `04-KAWAI DISKS`
   - `Kawai_K5000R_manual.pdf` → 2 copies dans `01-DOCUMENTATION KAWAI` + 1 dans `03-KAWAI`

2. **Doublons d'archives ZIP/RAR** :
   - `kawai_cl36.rar` (148 Mo) → dans `02-SOUNDS` ET `03-KAWAI`
   - `kawai_ex_pro.rar` (175 Mo) → dans `02-SOUNDS`, `03-KAWAI` ET `04-KAWAI`
   - `K5000_EAJ_BANKS_1-14.zip` → dans `03-KAWAI`, `04-KAWAI`, `04-KAWAI DISKS`
   - `SoundDiver_Kawai_K5000_OEM.zip` → dans racine, `01-KAWAI`, `KAWAI`, `03-SOFTWARE`, `KAWAI K5000`
   - `k5keditorV0.75.zip` → dans `01-KAWAI` ET `04-KAWAI`

3. **Archives décompressées à côté de leur ZIP** - ZIP + dossier extrait coexistent partout

4. **Doublons de logiciels** :
   - SoundDiver : 5+ copies (répertoires + zips)
   - k5kcuis.exe : 3 copies (`01-KAWAI`, `03-KAWAI`, `KAWAI`)
   - MidiQuest : 7 versions/doublons dans `03-SOFTWARE` (~830 Mo !)
   - k5keditor : versions 0.75, 0.77.2, A4

5. **Nommage incohérent** des dossiers racine :
   - `01-KAWAI`, `03-KAWAI`, `04-KAWAI` → tentatives successives d'organisation ?
   - `KAWAI`, `KAWAI K5000` → noms génériques
   - `collect2`, `collect2_2`, `k5kcol2` → même collection "Collect2"

6. **Données non-K5000** mélangées :
   - `kawai_cl36.rar` → piano numérique Kawai CL36
   - `kawai_ex_pro.rar` → piano numérique Kawai EX Pro
   - fichiers `.PCG` → format Korg

---

## Structure cible proposée

```
D:\01-MUSIQUE\03-KAWAI\
│
├── 01-DOCUMENTATION\
│   ├── manuels\
│   │   ├── Kawai_K5000S_Manual.pdf
│   │   ├── Kawai_K5000S_Manual_FR.pdf        (mode d'emploi FR)
│   │   ├── Kawai_K5000R_Manual.pdf
│   │   ├── Kawai_K5000W_Manual.pdf
│   │   ├── Kawai_K5000_MIDI_Implementation.pdf
│   │   └── Kawai_K5000_Service_Manual.pdf
│   ├── guides\
│   │   ├── kawai_k5000_wizoo_part1.pdf
│   │   └── kawai_k5000_wizoo_part2.pdf
│   ├── tips\                                  (K5000tip)
│   └── web-resources\                         (htm, html sauvegardés)
│
├── 02-PATCHES\
│   ├── factory\
│   │   ├── v1\                               (v1 factory)
│   │   └── v3\                               (v3 factory)
│   ├── banks\
│   │   ├── EAJ_BANKS_1-14\
│   │   ├── supplement40S\
│   │   └── Kawai_K5000W_SupplementDisk\
│   ├── collections\
│   │   ├── collect2\                          (Collect2 - KA1 + KAA + KCA)
│   │   ├── K5000archive\
│   │   ├── alternateSoundCollection\
│   │   └── Kawai_K5000_Ugo\
│   └── sound-designers\                       (patches par auteur)
│       ├── k5kbass\
│       ├── k5kcarty\
│       ├── k5kchris\
│       ├── k5kgeof\
│       ├── k5khansn\
│       ├── k5kisvah\
│       ├── k5kjensg\
│       ├── k5kkenji\
│       ├── k5kleitr\
│       ├── k5kmattj\
│       ├── k5kmkniat\
│       ├── k5knicho\
│       ├── k5koldk\
│       ├── k5kpfava\
│       ├── k5kphonk\
│       ├── k5krobrt\
│       ├── k5ksasch\
│       ├── k5ksumma\
│       ├── k5ktaylr\
│       ├── k5kwall\
│       ├── k5kwesj\
│       ├── k5kxaza\
│       └── k5kyitz2\
│
├── 03-SAMPLES-KSF\                           (fichiers .KSF volumineux)
│   ├── K5000_Wizoo_Disk\
│   └── (autres collections KSF)
│
├── 04-SOFTWARE\
│   ├── editors\
│   │   ├── k5keditor_v0.75\
│   │   ├── k5keditor_v0.77.2\
│   │   ├── k5keditor_A4\
│   │   ├── k5kcuis\
│   │   └── JSynthLib\
│   ├── sounddiver\
│   │   ├── SoundDiver_K5000_OEM\             (version OEM Kawai)
│   │   └── SoundDiver_v3.0.5.4\             (version complète)
│   ├── midiquest\                            (garder 1 seule version)
│   │   └── MidiQuestPro_v12_x64\
│   └── drivers\
│       └── usb_midi_driver\
│
├── 05-GOTEK-HFE\                             (images disquettes pour Gotek)
│   └── Kawai_K5000_Gotek_Collection_V1.0\
│
├── 06-MIDI-FILES\                            (fichiers .mid, .syx)
│
├── _ARCHIVES\                                (ZIPs/RARs originaux, référence)
│   └── (tous les .zip et .rar, 1 seule copie)
│
└── _HORS-K5000\                              (données non-K5000 à déplacer ailleurs)
    ├── kawai_cl36\
    └── kawai_ex_pro\
```

---

## Actions à effectuer

### Phase 1 - Nettoyage immédiat (sans perte)
- [ ] Identifier et lister tous les doublons exacts (par hash MD5)
- [ ] Séparer les données non-K5000 (CL36, EX Pro)

### Phase 2 - Réorganisation
- [ ] Créer la nouvelle arborescence
- [ ] Déplacer les fichiers uniques vers la structure cible
- [ ] Consolider les doublons (garder 1 copie)

### Phase 3 - Nettoyage final
- [ ] Supprimer les dossiers vides
- [ ] Vérifier l'intégrité (nombre de fichiers, tailles)

---

## Estimations d'espace récupéré

| Catégorie | Doublons estimés |
|---|---|
| PDFs en double | ~50 Mo |
| kawai_cl36.rar x2 | ~148 Mo |
| kawai_ex_pro.rar x2 | ~175 Mo |
| SoundDiver x4 | ~105 Mo |
| MidiQuest doublons | ~570 Mo |
| ZIPs en double divers | ~50 Mo |
| **Total estimé** | **~1.1 Go** |
