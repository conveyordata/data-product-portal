/*The purpose of this script is to check if the errors defined in api-errors.ts match the errors reported
in the OpenAPI specification.
 */
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const currentFilePath = fileURLToPath(import.meta.url);
const currentDirectory = path.dirname(currentFilePath);
const apiErrorsPath = path.resolve(currentDirectory, '../src/store/common/api-errors.ts');
const openApiPath = path.resolve(currentDirectory, '../../docs/static/openapi.json');

function extractErrorDefinitions(content) {
    const pattern = /export const (\w+)\s*=\s*(['"])([\s\S]*?)\2\s*;/g;
    const definitions = [];

    for (const match of content.matchAll(pattern)) {
        definitions.push({
            name: match[1],
            detail: match[3],
        });
    }

    return definitions;
}

function is4xxResponse(statusCode) {
    return /^4\d\d$/.test(statusCode);
}

function addResponseContentDetails(content, details) {
    if (!content || typeof content !== 'object') {
        return;
    }

    for (const mediaType of Object.values(content)) {
        if (!mediaType || typeof mediaType !== 'object') {
            continue;
        }

        const exampleDetail = mediaType.example?.detail;
        if (typeof exampleDetail === 'string') {
            details.add(exampleDetail);
        }

        const examples = mediaType.examples;
        if (!examples || typeof examples !== 'object') {
            continue;
        }

        for (const example of Object.values(examples)) {
            const detail = example?.value?.detail;
            if (typeof detail === 'string') {
                details.add(detail);
            }
        }
    }
}

function collectResponseErrorDetails(openApi) {
    const details = new Set();

    for (const pathItem of Object.values(openApi.paths ?? {})) {
        if (!pathItem || typeof pathItem !== 'object') {
            continue;
        }

        for (const operation of Object.values(pathItem)) {
            if (!operation || typeof operation !== 'object') {
                continue;
            }

            const responses = operation.responses;
            if (!responses || typeof responses !== 'object') {
                continue;
            }

            for (const [statusCode, response] of Object.entries(responses)) {
                if (!is4xxResponse(statusCode)) {
                    continue;
                }

                addResponseContentDetails(response?.content, details);
            }
        }
    }

    return details;
}

async function validateApiErrors() {
    const [apiErrorsContent, openApiContent] = await Promise.all([
        readFile(apiErrorsPath, 'utf-8'),
        readFile(openApiPath, 'utf-8'),
    ]);

    const definitions = extractErrorDefinitions(apiErrorsContent);

    if (definitions.length === 0) {
        throw new Error(`No exported API error constants found in ${apiErrorsPath}.`);
    }

    const openApi = JSON.parse(openApiContent);
    const exampleDetails = collectResponseErrorDetails(openApi);
    const missingDefinitions = definitions.filter(({ detail }) => !exampleDetails.has(detail));

    if (missingDefinitions.length > 0) {
        const missingList = missingDefinitions.map(({ name, detail }) => `- ${name}: "${detail}"`).join('\n');
        throw new Error(`API error definitions missing from OpenAPI examples:\n${missingList}`);
    }

    console.log(`Validated ${definitions.length} API error definitions against OpenAPI examples.`);
}

validateApiErrors().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exit(1);
});
