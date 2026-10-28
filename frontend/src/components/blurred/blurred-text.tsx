import { Typography } from 'antd';
import type { ComponentProps } from 'react';

export default function BlurredText({ style, ...props }: ComponentProps<typeof Typography.Text>) {
    return (
        <Typography.Text
            {...props}
            style={{
                ...style,
                filter: 'blur(0.35em)',
                userSelect: 'none',
            }}
        />
    );
}
