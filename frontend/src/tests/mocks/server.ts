import { setupServer } from 'msw/node';
import { handlers } from '@/tests/mocks/handlers';

export const server = setupServer(...handlers);
