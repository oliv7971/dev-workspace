#!/usr/bin/env python3
# midistyle_toolkit.py
# (c) 2025 — conçu pour aider à auditer, préparer et baliser des SMF en vue d'une conversion PA4X.
# Nécessite: mido, pyyaml

import argparse
import csv
import logging
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import yaml
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo, tempo2bpm

# ------------- classes utilitaires -------------

class TimeTracker:
    """Gère la conversion entre temps absolu et temps delta pour les messages MIDI."""
    
    def __init__(self):
        self.track_times: Dict[str, int] = {}  # temps absolu par track
    
    def get_delta(self, track_id: str, absolute_time: int) -> int:
        """
        Calcule le delta time pour un message basé sur le temps absolu.
        
        Args:
            track_id: Identifiant unique de la track
            absolute_time: Temps absolu du message
            
        Returns:
            Delta time à utiliser pour le message
        """
        last_time = self.track_times.get(track_id, 0)
        delta = max(0, absolute_time - last_time)
        self.track_times[track_id] = absolute_time
        return delta
    
    def reset_track(self, track_id: str):
        """Remet à zéro le temps pour une track."""
        self.track_times[track_id] = 0

# ------------- utils -------------

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure le système de logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)

def validate_midi_file(path: Path) -> bool:
    """
    Valide qu'un fichier MIDI peut être lu correctement.
    
    Args:
        path: Chemin vers le fichier MIDI
        
    Returns:
        True si le fichier est valide, False sinon
    """
    try:
        mf = MidiFile(path)
        # Vérifications basiques
        if len(mf.tracks) == 0:
            logging.warning(f"Fichier MIDI vide: {path}")
            return False
        if mf.ticks_per_beat <= 0:
            logging.warning(f"PPQ invalide dans {path}: {mf.ticks_per_beat}")
            return False
        return True
    except Exception as e:
        logging.error(f"Erreur lecture MIDI {path}: {e}")
        return False

def load_config(p: Optional[Path]) -> dict:
    if p is None:
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def pp_time_sig(num: int, den: int) -> str:
    return f"{num}/{den}"

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def map_channel_to_role(channel: int, note: Optional[int] = None, 
                       note_stats: Optional[Dict[int, List[int]]] = None) -> str:
    """
    Détermine le rôle d'un canal MIDI basé sur le canal et les caractéristiques des notes.
    
    Args:
        channel: Canal MIDI (0-15)
        note: Note MIDI (optionnel, pour affiner la détection)
        note_stats: Statistiques des notes par canal pour détecter la basse
    
    Returns:
        Rôle assigné: 'drum', 'bass', 'acc1', etc.
    """
    # Canal de batterie GM standard
    if channel == 9:
        return "drum"
    
    # Détection de basse basée sur les statistiques des notes
    if note_stats and channel in note_stats:
        notes = note_stats[channel]
        if len(notes) >= 8:  # Assez de données pour analyser
            median_note = sorted(notes)[len(notes)//2]
            note_range = max(notes) - min(notes)
            
            # Critères pour identifier une ligne de basse
            if median_note < 55 and note_range < 24:  # Notes graves, gamme limitée
                return "bass"
    
    # Fallback basé sur la note individuelle
    if note is not None and note < 48:  # Notes très graves
        return "bass"
    
    # Par défaut, assigner à acc1 (ou rotation intelligente plus tard)
    return "acc1"

def detect_bass_channel(note_stats: Dict[int, List[int]]) -> Optional[int]:
    """
    Détecte le canal le plus susceptible d'être la basse.
    
    Args:
        note_stats: Dictionnaire {canal: [notes...]}
    
    Returns:
        Canal de basse détecté ou None
    """
    best_channel = None
    best_score = -1
    
    for channel, notes in note_stats.items():
        if channel == 9 or len(notes) < 4:  # Ignorer batterie et canaux avec peu de notes
            continue
            
        # Calcul du score de "bassiness"
        median_note = sorted(notes)[len(notes)//2]
        note_range = max(notes) - min(notes)
        note_density = len(notes) / len(set(notes))  # Répétition des notes
        
        # Score basé sur: notes graves + gamme limitée + répétitions
        score = 0
        if median_note < 55:  # Notes graves
            score += 3
        if median_note < 48:  # Très graves
            score += 2
        if note_range < 24:   # Gamme limitée
            score += 2
        if note_density > 1.5:  # Notes répétées
            score += 1
            
        if score > best_score:
            best_score = score
            best_channel = channel
    
    return best_channel if best_score >= 3 else None

# ------------- AUDIT -------------

def audit_midi(path: Path, cfg: dict) -> dict:
    """Analyse un fichier MIDI et retourne un rapport détaillé."""
    logger = logging.getLogger(__name__)
    
    if not validate_midi_file(path):
        return {"file": str(path), "error": "Fichier MIDI invalide", "candidate_score": 0}
    
    try:
        mf = MidiFile(path)
        ppq = mf.ticks_per_beat
        logger.debug(f"Analyse de {path} (PPQ: {ppq})")

        tempo_map = []
        time_sigs = set()
        program_changes = 0
        has_drum = False
        drum_hits = 0
        unique_channels = set()
        track_count = len(mf.tracks)
        cc_count_total = 0
        pb_range_est = 0  # approx amplitude in semitones if possible

        # rough bass detector: lowest median note channel (excluding channel 9/10 indexing 0-based? mido uses 0..15, GM drum = 9)
        note_stats: Dict[int, List[int]] = {}

        # tempo default
        current_tempo = 500000  # 120 bpm
        tempo_changes = 0

        for ti, tr in enumerate(mf.tracks):
            current_notes_on = {}
            for msg in tr:
                if msg.is_meta:
                    if msg.type == "set_tempo":
                        tempo_map.append(msg.tempo)
                        tempo_changes += 1
                    elif msg.type == "time_signature":
                        time_sigs.add(pp_time_sig(msg.numerator, msg.denominator))
                    continue

                if msg.type == "program_change":
                    program_changes += 1

                if msg.type in ("control_change",):
                    cc_count_total += 1

                if msg.type == "pitchwheel":
                    # crude estimator in semitones (assuming ±8192 maps to ±2 semitones if no RPN), but we'll just track amplitude
                    pb_semitones = abs(msg.pitch) / 8192.0 * 2.0
                    pb_range_est = max(pb_range_est, pb_semitones)

                if msg.type in ("note_on", "note_off"):
                    ch = msg.channel
                    unique_channels.add(ch)
                    if ch == 9:  # GM Drum
                        if msg.type == "note_on" and msg.velocity > 0:
                            has_drum = True
                            drum_hits += 1
                    else:
                        if msg.type == "note_on" and msg.velocity > 0:
                            note_stats.setdefault(ch, []).append(msg.note)

        # Utilisation de la nouvelle fonction de détection de basse
        bass_channel = detect_bass_channel(note_stats)
        bass_median = 0
        bass_monophony_score = 0.0
        
        if bass_channel is not None:
            notes = note_stats[bass_channel]
            notes_sorted = sorted(notes)
            bass_median = notes_sorted[len(notes_sorted)//2]
            
            # Score de monophonie amélioré
            density = len(notes)
            uniq = len(set(notes))
            bass_monophony_score = (uniq / max(1, density))

        # Compute score
        thresholds = cfg.get("audit_thresholds", {})
        ts_ok = any(ts in thresholds.get("allowed_time_sigs", ["4/4", "2/4", "6/8"]) for ts in (time_sigs or {"4/4"}))
        score = 100.0
        score -= max(0, tempo_changes - thresholds.get("max_tempo_changes", 1)) * 10
        score -= 0 if ts_ok else 15
        score -= max(0, program_changes - thresholds.get("max_program_changes_total", 6)) * 2
        score -= max(0, track_count - thresholds.get("max_tracks", 12)) * 1.5
        score -= max(0, len(unique_channels) - thresholds.get("max_unique_channels", 10)) * 1.5
        score -= 15 if not has_drum else 0
        score -= 10 if drum_hits < thresholds.get("min_drum_hits", 8) else 0
        score -= max(0, pb_range_est - thresholds.get("max_pitch_bend_range", 4)) * 4

        score = clamp(round(score, 1), 0, 100)
        
        logger.debug(f"Score calculé pour {path}: {score}")

        return {
            "file": str(path),
            "ppq": ppq,
            "tempo_changes": tempo_changes,
            "time_sigs": ";".join(sorted(time_sigs)) if time_sigs else "unknown",
            "program_changes": program_changes,
            "has_drum": int(has_drum),
            "drum_hits": drum_hits,
            "tracks": track_count,
            "unique_channels": len(unique_channels),
            "est_pb_range": round(pb_range_est, 2),
            "bass_channel": bass_channel if bass_channel is not None else "",
            "bass_median_note": bass_median if bass_channel is not None else "",
            "bass_mono_score": round(bass_monophony_score, 3) if bass_channel is not None else "",
            "candidate_score": score,
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de {path}: {e}")
        return {"file": str(path), "error": str(e), "candidate_score": 0}

def cmd_audit(args):
    """Commande d'audit avec logging amélioré."""
    logger = setup_logging()
    cfg = load_config(Path(args.config) if args.config else None)
    inputs = []
    p = Path(args.path)
    
    if p.is_dir():
        inputs = sorted(p.rglob("*.mid"))
        logger.info(f"Trouvé {len(inputs)} fichiers MIDI dans {p}")
    else:
        inputs = [p]
        logger.info(f"Analyse du fichier {p}")

    rows = []
    for i, f in enumerate(inputs, 1):
        logger.info(f"Traitement {i}/{len(inputs)}: {f.name}")
        try:
            rows.append(audit_midi(f, cfg))
        except Exception as e:
            logger.error(f"Erreur sur {f}: {e}")
            rows.append({"file": str(f), "error": str(e), "candidate_score": 0})

    if not rows:
        logger.error("Aucun fichier traité avec succès")
        return

    out = Path(args.out or "audit_report.csv")
    with open(out, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    
    # Statistiques
    valid_scores = [r.get("candidate_score", 0) for r in rows if "error" not in r]
    if valid_scores:
        avg_score = sum(valid_scores) / len(valid_scores)
        logger.info(f"Score moyen: {avg_score:.1f}")
        logger.info(f"Meilleur score: {max(valid_scores)}")
    
    logger.info(f"Rapport sauvé: {out}")

# ------------- PREPARE (clean + map + quantize + markers) -------------

def quantize_ticks(ticks: int, grid: int) -> int:
    return round(ticks / grid) * grid

def build_marker(text: str, time: int) -> MetaMessage:
    return MetaMessage("marker", text=text, time=time)

def cmd_prepare(args):
    """Nettoie, mappe et quantifie un fichier MIDI avec les améliorations."""
    logger = setup_logging()
    cfg = load_config(Path(args.config) if args.config else None)
    
    if not validate_midi_file(Path(args.input)):
        logger.error(f"Fichier MIDI invalide: {args.input}")
        return
    
    mf = MidiFile(args.input)
    ppq = mf.ticks_per_beat
    prep = cfg.get("prepare", {})
    q_div = int(prep.get("quantize_division", 16))
    grid = int(round(ppq * 4 / q_div))  # e.g., 16 => 1/16
    
    logger.info(f"Traitement de {args.input} (PPQ: {ppq}, grille: {grid})")

    out_mf = MidiFile(ticks_per_beat=ppq)
    section_markers = cfg.get("section_markers", {})
    chmap = cfg.get("channels", {})
    names = cfg.get("korg_track_names", {})

    # Create one track per role to simplify
    roles = ["drum","perc","bass","acc1","acc2","acc3","acc4","acc5"]
    tr_by_role = {r: MidiTrack() for r in roles}
    for r in roles:
        t = tr_by_role[r]
        t.append(MetaMessage("track_name", name=names.get(r, r.upper()), time=0))
        out_mf.tracks.append(t)

    # Pré-analyse pour détecter la basse
    note_stats: Dict[int, List[int]] = {}
    for tr in mf.tracks:
        for msg in tr:
            if msg.type == "note_on" and msg.velocity > 0 and msg.channel != 9:
                note_stats.setdefault(msg.channel, []).append(msg.note)
    
    # Utiliser TimeTracker pour gérer les temps
    time_tracker = TimeTracker()
    for role in roles:
        time_tracker.reset_track(role)

    # Processing avec la nouvelle logique
    for ti, tr in enumerate(mf.tracks):
        abs_time = 0
        for msg in tr:
            abs_time += msg.time
            if msg.is_meta:
                continue
            if msg.type in ("sysex",) and not prep.get("keep_sysex", False):
                continue
            if msg.type in ("aftertouch","polytouch") and not prep.get("keep_aftertouch", False):
                continue

            m = msg.copy()
            
            # Nouveau mapping intelligent des canaux
            if hasattr(m, "channel"):
                old_channel = m.channel
                role = map_channel_to_role(old_channel, getattr(m, "note", None), note_stats)
                
                # Mapper vers le canal approprié selon le rôle
                if role == "drum":
                    m.channel = chmap.get("drum", 10) - 1  # mido uses 0-15
                elif role == "bass":
                    m.channel = chmap.get("bass", 2) - 1
                else:  # acc1, acc2, etc.
                    m.channel = chmap.get(role, 3) - 1

            # velocity clamp
            if m.type == "note_on" and m.velocity > 0:
                vmin, vmax = prep.get("velocity_minmax",[1,120])
                m.velocity = clamp(m.velocity, vmin, vmax)

            # pitchbend amplitude soft-limit (no RPN writing here)
            if m.type == "pitchwheel":
                limit = int(8192 * prep.get("limit_pitch_bend_semitones",2) / 2.0)
                m.pitch = int(clamp(m.pitch, -limit, limit))

            # quantize time (delta-based rebuild using absolute grid)
            q_abs = quantize_ticks(abs_time, grid)

            # route to track by role
            role = map_channel_to_role(getattr(m, "channel", 0), getattr(m, "note", None), note_stats)
            t = tr_by_role.get(role, tr_by_role["acc1"])

            # utiliser TimeTracker pour calculer le delta
            delta = time_tracker.get_delta(role, q_abs)
            m.time = delta
            t.append(m)

    # Add optional section markers at t=0 so Korg can segment (user can move later in a DAW)
    for key, txt in section_markers.items():
        tr_by_role["drum"].append(build_marker(txt, time=0))

    out = Path(args.out or "prepared.mid")
    out_mf.save(out)
    logger.info(f"Fichier traité sauvé: {out}")

# ------------- BUILD KORG PACK (from Yamaha MIDI exports) -------------

def cmd_build_korg(args) -> None:
    """
    Attend un dossier avec des sous-dossiers nommés comme les sections Korg
    (Intro1, Var1..4, Fill1..4, Break, Ending1..3), chacun contenant un ou plusieurs SMF.
    Le script concatène chaque sous-dossier en une section et insère un 'marker' correspondant.
    """
    logger = setup_logging()
    cfg = load_config(Path(args.config) if args.config else None)
    
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Dossier d'entrée introuvable: {input_path}")
        return
    
    sections = [
        ("intro1","Intro 1"),
        ("intro2","Intro 2"),
        ("intro3","Intro 3"),
        ("var1","Var 1"),
        ("var2","Var 2"),
        ("var3","Var 3"),
        ("var4","Var 4"),
        ("fill1","Fill 1"),
        ("fill2","Fill 2"),
        ("fill3","Fill 3"),
        ("fill4","Fill 4"),
        ("break","Break"),
        ("ending1","Ending 1"),
        ("ending2","Ending 2"),
        ("ending3","Ending 3"),
    ]
    sec_names = cfg.get("section_markers", {})
    # master file
    out_mf = MidiFile(ticks_per_beat=480)
    main = MidiTrack()
    out_mf.tracks.append(main)

    cur_abs = 0
    sections_found = 0
    
    for key, fallback in sections:
        folder = input_path / key.capitalize()  # e.g., Var1
        label = sec_names.get(key, fallback)
        if not folder.exists():
            logger.debug(f"Section {key} non trouvée: {folder}")
            continue
            
        midi_files = list(folder.glob("*.mid"))
        if not midi_files:
            logger.warning(f"Aucun fichier MIDI dans {folder}")
            continue
            
        logger.info(f"Traitement section {label}: {len(midi_files)} fichiers")
        sections_found += 1
        
        # marker
        main.append(MetaMessage("marker", text=label, time=0))
        # append all midis in that folder, serialized
        for smf in sorted(midi_files):
            if validate_midi_file(smf):
                mf = MidiFile(smf)
                # naive merge into 'main' track with delta alignment
                abs_time = cur_abs
                for tr in mf.tracks:
                    tacc = cur_abs
                    for msg in tr:
                        tacc += msg.time
                        m = msg.copy(time=msg.time)
                        main.append(m)
                # add 1 beat of gap between clips
                main.append(Message("note_off", channel=0, note=0, velocity=0, time=int(out_mf.ticks_per_beat)))

        # update current absolute (approx): add 4 bars @ 4/4 by default so sections don't overlap
        cur_abs += int(out_mf.ticks_per_beat * 16)

    if sections_found == 0:
        logger.error("Aucune section trouvée - vérifiez la structure des dossiers")
        return
        
    out = Path(args.out or "korg_ready.mid")
    out_mf.save(out)
    logger.info(f"Pack Korg créé avec {sections_found} sections: {out}")

# ------------- CLI -------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Audit, préparer et baliser des SMFs pour Korg PA4X")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="Scanner un dossier de .mid et sortir un CSV")
    a.add_argument("path")
    a.add_argument("--out", default="audit_report.csv")
    a.add_argument("--config")
    a.set_defaults(func=cmd_audit)

    p = sub.add_parser("prepare", help="Nettoyer/mapper/quantifier un SMF et ajouter des marqueurs")
    p.add_argument("input")
    p.add_argument("--out", default="prepared.mid")
    p.add_argument("--config")
    p.set_defaults(func=cmd_prepare)

    b = sub.add_parser("build-korg-pack", help="Assembler des exports Yamaha (MIDI) en un seul SMF balisé")
    b.add_argument("input", help="Dossier racine contenant Intro1, Var1..4, Fill1..4, Break, Ending1..3")
    b.add_argument("--out", default="korg_ready.mid")
    b.add_argument("--config")
    b.set_defaults(func=cmd_build_korg)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
