import type { User } from '@/store/api/services/generated/usersApi.ts';

export function cleanupForSearching(value: string): string {
    return value
        .toLowerCase()
        ?.normalize('NFD')
        .replace(/\p{Diacritic}/gu, '')
        .toLowerCase();
}

export function searchMatchesUser(search: string, user: User): boolean {
    const cleanedSearch = cleanupForSearching(search);
    return (
        cleanupForSearching(user?.email)?.includes(cleanedSearch) ||
        cleanupForSearching(user?.first_name).includes(cleanedSearch) ||
        cleanupForSearching(user?.last_name).includes(cleanedSearch)
    );
}
