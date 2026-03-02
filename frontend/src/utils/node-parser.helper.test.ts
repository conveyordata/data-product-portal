import { Position } from '@xyflow/react';
import { describe, expect, it, vi } from 'vitest';

import type { Node as GraphNode } from '@/store/api/services/generated/dataProductsApi';
import { parseRegularNode, sharedAttributes } from './node-parser.helper';

// Minimal GraphNode factory — only fields the parser actually reads.
// `import type` is erased at compile time so it does not trigger module execution.
const graphNode = (domain_id: string | null = null, domain: string | null = null): GraphNode => ({
    id: 'node-1',
    type: 'dataProductNode' as GraphNode['type'],
    isMain: false,
    data: {
        id: 'node-1',
        name: 'Test Product',
        icon_key: 'ANALYTICS',
        domain_id,
        domain,
        description: null,
        link_to_id: null,
    },
});

const noop = vi.fn();

// ---------------------------------------------------------------------------
// parentId assignment (the core change this PR makes)
// ---------------------------------------------------------------------------

describe('sharedAttributes — domainsEnabled', () => {
    it('sets parentId to domain_id when domainsEnabled=true and domain_id is present', () => {
        const node = sharedAttributes(graphNode('dom-1', 'Finance'), noop, true, false);
        expect(node.parentId).toBe('dom-1');
    });

    it('does not set parentId when domainsEnabled=false even if domain_id is present', () => {
        const node = sharedAttributes(graphNode('dom-1', 'Finance'), noop, false, false);
        expect(node.parentId).toBeUndefined();
    });

    it('does not set parentId when domain_id is null', () => {
        const node = sharedAttributes(graphNode(null, null), noop, true, false);
        expect(node.parentId).toBeUndefined();
    });

    it('always sets id, position, type from the input node', () => {
        const node = sharedAttributes(graphNode('dom-1', 'Finance'), noop, true, false);
        expect(node.id).toBe('node-1');
        expect(node.position).toEqual({ x: 0, y: 0 });
        expect(node.type).toBe('dataProductNode');
    });
});

// ---------------------------------------------------------------------------
// parseRegularNode passes extra_attributes through
// ---------------------------------------------------------------------------

describe('parseRegularNode', () => {
    it('merges extra_attributes into data', () => {
        const extra = { targetHandlePosition: Position.Left };
        const node = parseRegularNode(graphNode('dom-1', 'Finance'), noop, true, false, extra);
        expect(node.data.targetHandlePosition).toBe('left');
    });

    it('preserves parentId set by sharedAttributes', () => {
        const node = parseRegularNode(graphNode('dom-1', 'Finance'), noop, true, false, {});
        expect(node.parentId).toBe('dom-1');
    });

    it('exposes the domain name on node.data.domain', () => {
        const node = parseRegularNode(graphNode('dom-1', 'Finance'), noop, true, false, {});
        expect(node.data.domain).toBe('Finance');
    });
});
