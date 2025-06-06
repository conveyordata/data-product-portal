import { message } from 'antd';
import type React from 'react';
import { useEffect } from 'react';
import { useSelector } from 'react-redux';

import { selectMessage } from '@/store/features/feedback/feedback-slice.ts';

const MessageListener: React.FC = () => {
    const { content, duration, onClose, type, id } = useSelector(selectMessage);
    const [messageApi, contextHolder] = message.useMessage({ maxCount: 5 });

    // biome-ignore lint: I don't know what the effect of removing id is
    useEffect(() => {
        if (content) {
            messageApi[type]({
                content,
                duration,
                onClose,
            });
        }
    }, [content, duration, type, id, messageApi, onClose]);

    return <>{contextHolder}</>;
};

export default MessageListener;
