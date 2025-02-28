#!/usr/bin/env bash

# Extract all router files and check their coverage
cd ./../backend
if poetry run python -c "
import xml.etree.ElementTree as ET
tree = ET.parse('coverage.xml')
root = tree.getroot()
files = [f for f in root.findall(\".//class\") if 'router' in f.get('name', '')]
failed = [f.get('name') for f in files if float(f.get('line-rate', 0)) < 1.0]
if failed:
print(f'❌ The following router files do not have 100% coverage: {failed}')
exit(1)
else:
print('✅ All router files have 100% coverage!')
"; then
    echo "Coverage check passed!"
else
    echo "Coverage check failed!"
    exit 1
fi
