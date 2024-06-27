import { useCallback, useState } from 'react';

export function useModal() {
    const [isVisible, setIsVisible] = useState(false);
    const handleOpen = useCallback(() => setIsVisible(true), []);
    const handleClose = useCallback(() => setIsVisible(false), []);

    return { isVisible, handleOpen, handleClose };
}
