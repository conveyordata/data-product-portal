import { readFile, writeFile } from 'node:fs/promises';

async function addTsNocheck() {
    const filePath = 'src/store/api/services/generated/completeServiceApi.ts';
    let content = await readFile(filePath, 'utf-8');

    // Remove any existing @ts-nocheck comments first to ensure idempotency
    content = content.replace(/^\/\/ @ts-nocheck\n/gm, '');

    // Add exactly one @ts-nocheck comment at the start
    const newContent = `// @ts-nocheck\n${content}`;
    await writeFile(filePath, newContent, 'utf-8');
}

addTsNocheck().catch(console.error);
