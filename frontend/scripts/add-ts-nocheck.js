import { readFileSync, writeFileSync } from 'node:fs';

const filePath = 'src/store/api/services/generated/completeServiceApi.ts';
const content = readFileSync(filePath, 'utf8');
const newContent = `// @ts-nocheck\n${content}`;
writeFileSync(filePath, newContent, 'utf8');
