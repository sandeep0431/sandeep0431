# Development Notes

This repository generates a GitHub profile README using local Python scripts and SVG-only animations. No JavaScript is required inside the README.

## 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 2. Install dependencies

For the full local workflow, including portrait generation:

```powershell
python -m pip install -r scripts/requirements-local.txt
```

For the GitHub Action contribution refresh only:

```powershell
python -m pip install -r scripts/requirements-action.txt
```

## 3. Add your photograph

Place your own portrait photo at the repository root:

```text
source-photo.jpg
```

The generator also accepts `source-photo.jpeg` and `source-photo.jpg.jpeg`, but `source-photo.jpg` is the preferred name for clarity.

Do not commit private or sensitive images unless you are comfortable making them public. Until this file exists, the portrait script writes a clear placeholder SVG.

## 4. Generate all assets

```powershell
python scripts/generate_all.py
```

This creates or refreshes:

```text
assets/contrib-heatmap.svg
assets/info-card.svg
assets/sandeep-ascii.svg
data/contributions.json
```

## 5. Preview locally

Open `README.md` in VS Code preview, or open the SVG files directly in a browser:

```text
assets/contrib-heatmap.svg
assets/info-card.svg
assets/sandeep-ascii.svg
```

GitHub will render the assets through relative paths such as `./assets/contrib-heatmap.svg`.

## 6. Test generation and validation

```powershell
python -m compileall scripts
python scripts/generate_all.py
python -c "import xml.etree.ElementTree as ET; [ET.parse(p) for p in ['assets/contrib-heatmap.svg','assets/info-card.svg','assets/sandeep-ascii.svg']]; print('svg xml ok')"
```

To verify scripts work from another directory:

```powershell
cd ..
python .\GITHUBREPO\scripts\generate_all.py
cd .\GITHUBREPO
```

## 7. Test GitHub Action logic locally

The workflow runs the contribution refresh path:

```powershell
python -m pip install -r scripts/requirements-action.txt
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

## 8. Push to GitHub

```powershell
git init
git add .
git commit -m "feat: add animated GitHub profile"
git branch -M main
git remote add origin https://github.com/sandeep0431/sandeep0431.git
git push -u origin main
```
