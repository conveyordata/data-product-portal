import { HttpResponse, http } from 'msw';
import { server } from './server.ts';

export const allowAllAuth = () => {
    server.use(
        http.get('*/api/v2/authz/roles/:scope', () => {
            return HttpResponse.json({ roles: [] });
        }),

        http.get('*/api/v2/authz/role_assignments/:data_product', () => {
            return HttpResponse.json({ role_assignments: [] });
        }),

        http.get('*/api/v2/authz/access/:action', () => {
            return HttpResponse.json({ allowed: true });
        }),
    );
};
