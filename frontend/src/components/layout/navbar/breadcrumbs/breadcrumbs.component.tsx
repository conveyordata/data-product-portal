import { HomeOutlined } from '@ant-design/icons';
import { Breadcrumb } from 'antd';
import type { BreadcrumbItemType } from 'antd/es/breadcrumb/Breadcrumb';
import { useTranslation } from 'react-i18next';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { BreadcrumbLink } from '@/components/layout/navbar/breadcrumbs/breadcrumb-link/breadcrumb-link.component.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';

export const Breadcrumbs = () => {
    const { breadcrumbs } = useBreadcrumbs();

    const { t } = useTranslation();

    const items: BreadcrumbItemType[] = breadcrumbs.map((crumb) => ({
        title: crumb.title,
        path: crumb.path,
    }));

    return (
        <Breadcrumb
            itemRender={(route, _params, routes) => {
                const isLast = routes.indexOf(route) === routes.length - 1;
                return <BreadcrumbLink to={route.path} isActive={isLast} title={route.title} />;
            }}
            items={[
                {
                    title: (
                        <>
                            <HomeOutlined />
                            {items.length === 0 ? t('Home') : ''}
                        </>
                    ),
                    path: ApplicationPaths.Home,
                },
                ...items,
            ]}
            separator={'/'}
        />
    );
};
