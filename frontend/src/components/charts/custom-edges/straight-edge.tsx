import { BaseEdge, type EdgeProps, getStraightPath } from '@xyflow/react';

export function StraightEdge({ id, sourceX, sourceY, targetX, targetY, style }: EdgeProps) {
    const [edgePath] = getStraightPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
    });

    const midX = (sourceX + targetX) / 2
    const midY = (sourceY + targetY) / 2

    // angle for arrow rotation
    const angle = Math.atan2(targetY - sourceY, targetX - sourceX) * (180 / Math.PI)

    return (
        <>
            <BaseEdge id={id} path={edgePath} style={style} />;
            {/* Arrow in the middle */}
            <polygon
                points="0,0 12,4 0,8 2,4"
                fill="currentColor"
                stroke="currentColor"
                strokeWidth="1"
                transform={`translate(${midX}, ${midY}) rotate(${angle}) translate(-6, -4)`}
                style={{
                fill: style?.stroke || "#b1b1b7",
                stroke: style?.stroke || "#b1b1b7",
                }}
            />
        </>
    );
}
