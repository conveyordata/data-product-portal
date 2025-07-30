import { BaseEdge, type EdgeProps, getStraightPath } from '@xyflow/react';

export function StraightEdge({ id, sourceX, sourceY, targetX, targetY, style }: EdgeProps) {
    const [edgePath] = getStraightPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
    });

    return <BaseEdge id={id} path={edgePath} style={style} />;
}
