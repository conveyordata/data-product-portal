import type { SchemaObjectResponse } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';

export type InferredRelationship = {
    id: string;
    sourceObjectId: string;
    sourcePropertyId: string;
    targetObjectId: string;
    targetPropertyId: string;
};

// Spike heuristic: no FK metadata exists yet, so relationships are inferred by name match against PKs; ambiguous matches are skipped.
export function inferRelationships(schemaObjects: SchemaObjectResponse[]): InferredRelationship[] {
    const primaryKeysByName = new Map<string, { objectId: string; propertyId: string }[]>();
    for (const object of schemaObjects) {
        for (const property of object.properties ?? []) {
            if (!property.primary_key) continue;
            const matches = primaryKeysByName.get(property.name) ?? [];
            matches.push({ objectId: object.id, propertyId: property.id });
            primaryKeysByName.set(property.name, matches);
        }
    }

    const relationships: InferredRelationship[] = [];
    for (const object of schemaObjects) {
        for (const property of object.properties ?? []) {
            if (property.primary_key) continue;
            const candidates = (primaryKeysByName.get(property.name) ?? []).filter(
                (candidate) => candidate.objectId !== object.id,
            );
            if (candidates.length !== 1) continue;
            const [target] = candidates;
            relationships.push({
                id: `${property.id}->${target.propertyId}`,
                sourceObjectId: object.id,
                sourcePropertyId: property.id,
                targetObjectId: target.objectId,
                targetPropertyId: target.propertyId,
            });
        }
    }
    return relationships;
}
