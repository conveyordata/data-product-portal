import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Home } from '@/pages/home/home.page.tsx';
import { DataProducts } from '@/pages/data-products/data-products.page.tsx';
import { DataProduct } from '@/pages/data-product/data-product.page.tsx';
import { Datasets } from '@/pages/datasets/datasets.page.tsx';
import { Dataset } from '@/pages/dataset/dataset.page.tsx';
import RootLayout from '@/components/layout/root/root.layout.tsx';
import { AuditLogs } from '@/pages/audit-logs/audit-logs.page.tsx';
import { Settings } from '@/pages/settings/settings.page.tsx';
import { ApplicationPaths } from '@/types/navigation';
import { DataProductCreate } from '@/pages/data-product-create/data-product-create.page.tsx';
import { AuthLayout } from '@/components/layout/auth/auth.layout.tsx';
import { DatasetCreate } from '@/pages/dataset-create/dataset-create.page.tsx';
import PublicLayout from '@/components/layout/public/public.layout.tsx';
import { Logout } from '@/pages/auth/logout/logout-page.tsx';
import { ErrorRootElement } from '@/pages/error/error-root-element.page.tsx';
import { DataProductEdit } from '@/pages/data-product-edit/data-product-edit.page.tsx';
import { DatasetEdit } from '@/pages/dataset-edit/dataset-edit.page.tsx';

const router = createBrowserRouter([
    {
        path: ApplicationPaths.Home,
        element: <AuthLayout />,
        errorElement: <ErrorRootElement />,
        children: [
            {
                path: ApplicationPaths.Home,
                element: <RootLayout />,
                children: [
                    {
                        path: ApplicationPaths.Home,
                        element: <Home />,
                        index: true,
                    },
                    {
                        path: ApplicationPaths.DataProducts,
                        children: [
                            {
                                element: <DataProducts />,
                                index: true,
                            },
                            {
                                path: ApplicationPaths.DataProduct,
                                element: <DataProduct />,
                            },
                            {
                                path: ApplicationPaths.DataProductNew,
                                element: <DataProductCreate />,
                            },
                            {
                                path: ApplicationPaths.DataProductEdit,
                                element: <DataProductEdit />,
                            },
                        ],
                    },

                    {
                        path: ApplicationPaths.Datasets,
                        children: [
                            {
                                element: <Datasets />,
                                index: true,
                            },
                            {
                                path: ApplicationPaths.Dataset,
                                element: <Dataset />,
                            },
                            {
                                path: ApplicationPaths.DatasetNew,
                                element: <DatasetCreate />,
                            },
                            {
                                path: ApplicationPaths.DatasetEdit,
                                element: <DatasetEdit />,
                            },
                        ],
                    },
                    {
                        path: ApplicationPaths.AuditLogs,
                        element: <AuditLogs />,
                    },
                    {
                        path: ApplicationPaths.Settings,
                        element: <Settings />,
                    },
                ],
            },
        ],
    },
    {
        path: ApplicationPaths.Home,
        element: <PublicLayout />,
        children: [
            {
                index: true,
                path: ApplicationPaths.Logout,
                element: <Logout />,
            },
        ],
    },
]);

export function AppRoutes() {
    return <RouterProvider router={router} />;
}
