import { describe, expect, it } from 'vitest';
import type { SchemaObjectResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import { inferRelationships } from './infer-relationships';

function object(id: string, name: string, properties: SchemaObjectResponse['properties']): SchemaObjectResponse {
    return { id, name, position: 1, properties };
}

describe('inferRelationships', () => {
    it('links a non-PK property to a uniquely-matching PK in another object', () => {
        const customers = object('customers', 'customers', [
            { id: 'customer_id', name: 'customer_id', position: 1, primary_key: true },
        ]);
        const orders = object('orders', 'orders', [
            { id: 'order_id', name: 'order_id', position: 1, primary_key: true },
            { id: 'orders.customer_id', name: 'customer_id', position: 2, primary_key: false },
        ]);

        const relationships = inferRelationships([customers, orders]);

        expect(relationships).toEqual([
            {
                id: 'orders.customer_id->customer_id',
                sourceObjectId: 'orders',
                sourcePropertyId: 'orders.customer_id',
                targetObjectId: 'customers',
                targetPropertyId: 'customer_id',
            },
        ]);
    });

    it('skips ambiguous matches where the same name is a PK in multiple objects', () => {
        const a = object('a', 'a', [{ id: 'a.id', name: 'id', position: 1, primary_key: true }]);
        const b = object('b', 'b', [{ id: 'b.id', name: 'id', position: 1, primary_key: true }]);
        const c = object('c', 'c', [{ id: 'c.id', name: 'id', position: 1, primary_key: false }]);

        expect(inferRelationships([a, b, c])).toEqual([]);
    });

    it('does not link a PK to itself within the same object', () => {
        const solo = object('solo', 'solo', [{ id: 'solo.id', name: 'id', position: 1, primary_key: true }]);

        expect(inferRelationships([solo])).toEqual([]);
    });
});
