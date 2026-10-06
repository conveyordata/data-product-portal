import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { server } from './mocks/server';

(globalThis as Record<string, unknown>).config = {
    API_BASE_URL: 'http://localhost:8080',
    OIDC_ENABLED: false,
    THEME_CONFIGURATION: 'bluethemeconfig',
    POSTHOG_ENABLED: false,
};

Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        dispatchEvent: () => false,
    }),
});

class ResizeObserverStub {
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
globalThis.ResizeObserver = ResizeObserverStub as unknown as typeof ResizeObserver;

beforeAll(() => {
    const { getComputedStyle } = window;
    window.getComputedStyle = (elt) => getComputedStyle(elt);
});

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
afterEach(() => {
    server.resetHandlers();
    cleanup();
});
afterAll(() => server.close());
