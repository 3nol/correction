Folder structure initializer:
```
find . -type d -maxdepth 1 -not -path './fuchs' -not -path './.git' -exec bash -c "mkdir {}/feedback; mkdir {}/concatenated" \;
```

