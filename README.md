Folder structure initializer:
```bash
find . -type d -maxdepth 1 -not -path './johannes.fuchs' -not -path './.git' -not -path '.' -exec bash -c "mkdir {}/feedback; mkdir {}/concatenated" \;
```

