import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll, vi } from 'vitest';
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
afterEach(async () => {
    // Ensure all pending timers created by UI libraries (for example useDelayState from
    // @rc-component/util) are ran. Those delayed callbacks can fire after jsdom teardown and attempt
    // to access window, which would otherwise throw ReferenceError: window is not defined.
    await vi.runAllTimersAsync();
    server.resetHandlers();
    cleanup();
});
afterAll(() => server.close());
