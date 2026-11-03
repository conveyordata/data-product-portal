import { Typography } from 'antd';
import type { ReactNode } from 'react';

const URL_PATTERN = /(https?:\/\/[^\s]*[^\s.,;:!?)\]'"])/;

export function linkify(text: string): ReactNode[] {
    let offset = 0;
    return text.split(URL_PATTERN).map((part, index) => {
        const start = offset;
        offset += part.length;
        return index % 2 === 1 ? (
            <Typography.Link key={start} href={part} target="_blank" rel="noopener noreferrer">
                {part}
            </Typography.Link>
        ) : (
            part
        );
    });
}
