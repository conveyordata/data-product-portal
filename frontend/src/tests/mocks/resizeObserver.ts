import { vi } from 'vitest';

export function stubResizeObserver() {
    let reportWidth: (width: number) => void = () => undefined;

    class ResizeObserverMock implements ResizeObserver {
        constructor(callback: ResizeObserverCallback) {
            reportWidth = (width) => callback([{ contentRect: { width } } as ResizeObserverEntry], this);
        }
        observe() {
            //do not remove
        }
        unobserve() {
            //do not remove
        }
        disconnect() {
            //do not remove
        }
    }

    vi.stubGlobal('ResizeObserver', ResizeObserverMock);
    return (width: number) => reportWidth(width);
}
