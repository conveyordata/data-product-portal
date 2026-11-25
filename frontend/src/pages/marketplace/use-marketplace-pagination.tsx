import { parseAsInteger, useQueryState } from 'nuqs';
import { useEffect, useRef } from 'react';

/**
 * Paginates `items` client-side, keeping the current page in the `page` URL query parameter.
 * Returns the page to show (always within range), a setter for it, and the items on that page.
 * When `pageSize` changes, it moves to the page that still holds the first item that was shown.
 * Pass `isLoaded` once `items` holds the real results, so an out-of-range page in the URL is corrected only then.
 */
export function useMarketplacePagination<T>(items: T[], pageSize: number, isLoaded: boolean) {
    const [requestedPage, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
    const lastPage = Math.max(1, Math.ceil(items.length / pageSize));
    const page = Math.min(Math.max(requestedPage, 1), lastPage);

    // When the page size changes, move to the page that holds the item that was shown first.
    // Otherwise, once the results are in, correct a page in the URL that is out of range.
    // One effect, so both cannot issue conflicting updates in the same render.
    const previousPageSize = useRef(pageSize);
    useEffect(() => {
        if (previousPageSize.current !== pageSize) {
            const firstVisibleItem = firstItemOf(requestedPage, previousPageSize.current);
            previousPageSize.current = pageSize;
            setPage(pageOf(firstVisibleItem, pageSize));
        } else if (isLoaded && page !== requestedPage) {
            setPage(page);
        }
    }, [isLoaded, page, pageSize, requestedPage, setPage]);

    const start = firstItemOf(page, pageSize);
    return { page, setPage, pageItems: items.slice(start, start + pageSize) };
}

function firstItemOf(page: number, pageSize: number) {
    return (page - 1) * pageSize;
}

function pageOf(itemIndex: number, pageSize: number) {
    return Math.floor(itemIndex / pageSize) + 1;
}
