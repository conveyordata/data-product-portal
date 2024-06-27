export function generateExternalIdFromName(name: string): string {
    return name.toLowerCase().trim().replace(/ /g, '-');
}
