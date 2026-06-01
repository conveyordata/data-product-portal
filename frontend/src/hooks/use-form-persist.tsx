import type { FormInstance } from 'antd';
import { useEffect, useRef, useState } from 'react';

export const useFormPersist = <T,>(form: FormInstance, storageKey: string) => {
    const hasPersistedData = useRef(localStorage.getItem(storageKey) !== null);
    const [isRestored, setIsRestored] = useState(!hasPersistedData.current);

    useEffect(() => {
        const savedData = localStorage.getItem(storageKey);
        if (savedData) {
            try {
                form.setFieldsValue(JSON.parse(savedData));
            } catch (error) {
                console.error('Failed to parse form data from localStorage', error);
            }
        }
        setIsRestored(true);
    }, [form, storageKey]);

    const onValuesChange = (_: Partial<T>, allValues: T) => {
        localStorage.setItem(storageKey, JSON.stringify(allValues));
    };

    const clearStorage = () => localStorage.removeItem(storageKey);

    return { onValuesChange, clearStorage, isRestored };
};
