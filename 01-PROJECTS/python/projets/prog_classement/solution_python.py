"""
SOLUTION au problème "python n'est pas reconnu"
Guide pour utiliser Python sur Windows
"""

print("🔧 DIAGNOSTIC PYTHON SUR WINDOWS")
print("="*50)

import sys
import os

print(f"✅ Python fonctionne !")
print(f"📍 Version: {sys.version}")
print(f"📁 Emplacement: {sys.executable}")
print(f"")

print("💡 SOLUTIONS POUR LANCER VOS SCRIPTS:")
print("="*50)

print("1️⃣ UTILISER 'py' au lieu de 'python':")
print("   py demo.py")
print("   py src/main.py")
print("   py test_simple.py")
print("")

print("2️⃣ OU utiliser le chemin complet:")
print(f"   \"{sys.executable}\" demo.py")
print("")

print("3️⃣ OU ajouter Python au PATH (permanent):")
print("   • Ouvrir Paramètres Windows")
print("   • Variables d'environnement")  
print("   • Modifier PATH")
print(f"   • Ajouter: {os.path.dirname(sys.executable)}")
print("")

print("🚀 POUR VOTRE PROGRAMME DE CLASSEMENT:")
print("="*45)
print("py demo.py                    ← Test du système")
print("py src/main.py               ← Programme principal")
print("py diagnostic.py             ← Vérification config")
print("")

print("⚠️  IMPORTANT:")
print("Sur Windows, 'py' est le lanceur officiel Python")
print("'python' ne fonctionne que si ajouté au PATH")

# Test des modules
print(f"\n🧪 TEST DES MODULES:")
modules_requis = ['os', 'shutil', 'json', 'logging', 'datetime']
for module in modules_requis:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError:
        print(f"   ❌ {module} (manquant)")

print(f"\n✅ Tout est prêt ! Utilisez 'py' pour lancer vos scripts.")