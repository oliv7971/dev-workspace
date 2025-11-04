"""
Test ultra simple - Sans imports complexes
"""

import os
import json

def test_basique():
    print("🧪 TEST BASIQUE")
    print("="*20)
    
    # Test config
    if os.path.exists("config/config.json"):
        try:
            with open("config/config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ Configuration OK")
            
            # Afficher les chemins
            print("\n📁 Chemins configurés:")
            for nom, chemin in config['chemins'].items():
                print(f"   {nom}: {chemin}")
                
        except Exception as e:
            print(f"❌ Erreur config: {e}")
    else:
        print("❌ Pas de configuration")
    
    print("\n🎯 Pour continuer:")
    print("1. Vérifiez/modifiez les chemins dans config/config.json")
    print("2. Lancez: python src/main.py")

if __name__ == "__main__":
    test_basique()
