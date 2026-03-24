// Define handlers that catch the corresponding requests and returns the mock data.
import { HttpResponse, http } from 'msw';

export const handlers = [
    http.get('*/api/v2/authz/roles/:scope', () => {
        return HttpResponse.json({ roles: [] });
    }),

    http.get('*/api/v2/authz/access/:action', () => {
        return HttpResponse.json({ allowed: true });
    }),
];
