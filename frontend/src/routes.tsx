import { NuqsAdapter } from 'nuqs/adapters/react-router/v7';
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router';
import { AuthLayout } from '@/components/layout/auth/auth.layout.tsx';
import PublicLayout from '@/components/layout/public/public.layout.tsx';
import RootLayout from '@/components/layout/root/root.layout.tsx';
import { AuditLogs } from '@/pages/audit-logs/audit-logs.page.tsx';
import { Logout } from '@/pages/auth/logout/logout-page.tsx';
import Cart from '@/pages/cart/cart.page.tsx';
import { DataProduct } from '@/pages/data-product/data-product.page.tsx';
import { DataProductCreate } from '@/pages/data-product-create/data-product-create.page.tsx';
import { DataProductEdit } from '@/pages/data-product-edit/data-product-edit.page.tsx';
import { DataProductsTable } from '@/pages/data-products/data-products-table.component.tsx';
import { Dataset } from '@/pages/dataset/dataset.page.tsx';
import { DatasetEdit } from '@/pages/dataset-edit/dataset-edit.page.tsx';
import { ErrorRootElement } from '@/pages/error/error-root-element.page.tsx';
import { ExplorerPage } from '@/pages/explorer/explorer.page.tsx';
import { Home } from '@/pages/home/home.page.tsx';
import { Marketplace } from '@/pages/marketplace/marketplace.page.tsx';
import { PeoplePage } from '@/pages/people/people-table.component.tsx';
import { ApplicationPaths } from '@/types/navigation';
import ProtectedRoute from './components/layout/protected/protected.layout.tsx';
import { DataOutput } from './pages/data-output/data-output.page.tsx';
import { DataOutputEdit } from './pages/data-output-edit/data-output-edit.page.tsx';
import { Settings } from './pages/settings/settings.page.tsx';

const router = createBrowserRouter([
    {
        path: ApplicationPaths.Home,
        element: (
            <NuqsAdapter>
                <AuthLayout />
            </NuqsAdapter>
        ),
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
                                element: <DataProductsTable />,
                                index: true,
                            },
                            {
                                path: ApplicationPaths.DataProduct,
                                element: <DataProduct />,
                            },
                            {
                                path: ApplicationPaths.DataOutput,
                                element: <DataOutput />,
                            },
                            {
                                path: ApplicationPaths.DataOutputEdit,
                                element: <DataOutputEdit />,
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
                        path: ApplicationPaths.Marketplace,
                        element: <Navigate to={ApplicationPaths.Datasets} />,
                    },
                    {
                        path: ApplicationPaths.MarketplaceCart,
                        children: [
                            {
                                element: <Cart />,
                                index: true,
                            },
                        ],
                    },
                    {
                        path: ApplicationPaths.Datasets,
                        children: [
                            {
                                element: <Marketplace />,
                                index: true,
                            },
                            {
                                path: ApplicationPaths.Dataset,
                                element: <Dataset />,
                            },
                            {
                                path: ApplicationPaths.DatasetEdit,
                                element: <DatasetEdit />,
                            },
                        ],
                    },
                    {
                        path: ApplicationPaths.People,
                        element: <PeoplePage />,
                    },
                    {
                        path: ApplicationPaths.AuditLogs,
                        element: <AuditLogs />,
                    },
                    {
                        path: ApplicationPaths.Explorer,
                        element: <ExplorerPage />,
                    },
                    {
                        path: ApplicationPaths.Settings,
                        element: <ProtectedRoute />,
                        children: [
                            {
                                index: true,
                                element: <Settings />,
                            },
                        ],
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
