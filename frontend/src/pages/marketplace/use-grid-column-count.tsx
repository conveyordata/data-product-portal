import { useEffect, useState } from 'react';

/**
 * Counts how many columns a `repeat(auto-fill, minmax(minColumnWidth, 1fr))` grid shows,
 * by measuring the element the returned `ref` is attached to.
 * Returns `fallback` until the element has been measured, and always at least 1.
 */
export function useGridColumnCount(minColumnWidth: number, gap: number, fallback: number) {
    const [element, setElement] = useState<HTMLElement | null>(null);
    const [columns, setColumns] = useState(fallback);

    useEffect(() => {
        if (!element) return;
        const observer = new ResizeObserver(([entry]) => {
            setColumns(Math.max(1, Math.floor((entry.contentRect.width + gap) / (minColumnWidth + gap))));
        });
        observer.observe(element);
        return () => observer.disconnect();
    }, [element, minColumnWidth, gap]);

    return { ref: setElement, columns };
}
