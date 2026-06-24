# Packaging PDF Presenter

## macOS (.app)
Sur un Mac (Intel ou Apple Silicon) :
```bash
bash packaging/build_macos.sh
```
Résultat : `dist/PDF Presenter.app` + `dist/PDF-Presenter-macOS.zip`.
Pour distribuer hors App Store, signez avec votre Developer ID puis notarisez :
```bash
codesign --deep --force --options runtime --sign "Developer ID Application: <Nom>" "dist/PDF Presenter.app"
xcrun notarytool submit dist/PDF-Presenter-macOS.zip --apple-id <…> --team-id <…> --wait
```

## Windows (.exe)
Sur Windows (PowerShell) :
```powershell
packaging\build_windows.ps1
```
Résultat : `dist\PDF Presenter\PDF Presenter.exe` + `dist\PDF-Presenter-Windows.zip`.

## Builds automatiques (recommandé)
Poussez le projet sur GitHub. Le workflow `.github/workflows/build.yml`
construit automatiquement le `.app` macOS ET le `.exe` Windows à chaque
tag `v*` (ex. `git tag v3.1 && git push --tags`). Les artefacts sont
disponibles dans l'onglet **Actions** de GitHub.

## Android — non supporté par cette base de code
PySide6 (Qt for Python) ne fournit pas de chemin officiel de packaging
Android. Pour Android il faut :
- **Réécrire l'UI en Kivy** (https://kivy.org) puis empaqueter avec
  Buildozer — la logique PyMuPDF reste réutilisable mais l'UI doit être
  refaite.
- Ou créer une **version web** (Flask/FastAPI + viewer PDF.js) et
  l'installer comme PWA sur le téléphone.
- Ou utiliser **BeeWare/Briefcase** (https://beeware.org), avec encore
  une réécriture de l'UI en Toga.
Aucune de ces options n'est un simple "build" du code actuel.

## Icônes (optionnel)
Posez `logo.icns` (macOS), `logo.ico` (Windows) ou `logo.png` à la racine
du projet — le spec PyInstaller les détectera automatiquement.
