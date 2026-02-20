import type { ReactNode } from 'react';
import { createContext, useContext, useState } from 'react';

export interface BreadcrumbItem {
    title: ReactNode;
    path?: string;
}

interface BreadcrumbContextType {
    breadcrumbs: BreadcrumbItem[];
    setBreadcrumbs: (breadcrumbs: BreadcrumbItem[]) => void;
}

const BreadcrumbContext = createContext<BreadcrumbContextType | undefined>(undefined);

export const BreadcrumbProvider = ({ children }: { children: ReactNode }) => {
    const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);

    return <BreadcrumbContext.Provider value={{ breadcrumbs, setBreadcrumbs }}>{children}</BreadcrumbContext.Provider>;
};

export const useBreadcrumbs = () => {
    const context = useContext(BreadcrumbContext);

    if (!context) {
        throw new Error('useBreadcrumbs must be used within BreadcrumbProvider');
    }

    return context;
};
