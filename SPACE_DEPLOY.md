# Deploying Aegis Runtime

## GitHub

Recommended repo name:

```text
aegis-runtime
```

From this folder:

```bash
git init
git add .
git commit -m "Build Aegis Runtime assistant demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/aegis-runtime.git
git push -u origin main
```

## Hugging Face Spaces

Create a new Space:

- Name: `aegis-runtime`
- SDK: Gradio
- Visibility: Public

Then push this folder:

```bash
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/aegis-runtime
git push space main
```

If using the Hugging Face CLI:

```bash
huggingface-cli login
huggingface-cli repo create aegis-runtime --type space --space_sdk gradio
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/aegis-runtime
git push space main
```
