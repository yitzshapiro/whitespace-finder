# Here's some useful stuff

script to print every file in a directory nicely:
```bash
for file in *.py *.txt; do if [ -f "$file" ]; then echo "$file:"; echo "\`\`\`"; cat "$file"; echo "\`\`\`"; fi; done
```

