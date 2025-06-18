import { createBrowserRouter, RouterProvider } from 'react-router';

import { AuthLayout } from '@/components/layout/auth/auth.layout.tsx';
import PublicLayout from '@/components/layout/public/public.layout.tsx';
import RootLayout from '@/components/layout/root/root.layout.tsx';
import { AuditLogs } from '@/pages/audit-logs/audit-logs.page.tsx';
import { Logout } from '@/pages/auth/logout/logout-page.tsx';
import { DataProduct } from '@/pages/data-product/data-product.page.tsx';
import { DataProductCreate } from '@/pages/data-product-create/data-product-create.page.tsx';
import { DataProductEdit } from '@/pages/data-product-edit/data-product-edit.page.tsx';
import { DataProducts } from '@/pages/data-products/data-products.page.tsx';
import { Dataset } from '@/pages/dataset/dataset.page.tsx';
import { DatasetCreate } from '@/pages/dataset-create/dataset-create.page.tsx';
import { DatasetEdit } from '@/pages/dataset-edit/dataset-edit.page.tsx';
import { Datasets } from '@/pages/datasets/datasets.page.tsx';
import { ErrorRootElement } from '@/pages/error/error-root-element.page.tsx';
import { ExplorerPage } from '@/pages/explorer/explorer.page.tsx';
import { Home } from '@/pages/home/home.page.tsx';
import { ApplicationPaths } from '@/types/navigation';

import ProtectedRoute from './components/layout/protected/protected.layout.tsx';
import { DataOutput } from './pages/data-output/data-output.page.tsx';
import { DataOutputEdit } from './pages/data-output-edit/data-output-edit.page.tsx';
import { EnvironmentConfig } from './pages/environment-config/environment-config.page.tsx';
import { EnvironmentConfigCreate } from './pages/environment-config-create/environment-config-create.page.tsx';
import { EnvironmentConfigs } from './pages/environment-configs/environment-configs.page.tsx';
import { EnvironmentCreate } from './pages/environment-create/environment-create.page.tsx';
import { Environments } from './pages/environments/environments.page.tsx';
import { PlatformServiceConfig } from './pages/platform-service-config/platform-service-config.page.tsx';
import { PlatformServiceConfigCreate } from './pages/platform-service-config-create/platform-service-config-create.page.tsx';
import { PlatformsConfigs } from './pages/platforms-configs/platforms-configs.page.tsx';
import { Settings } from './pages/settings/settings.page.tsx';
import { User } from './pages/user/user.page.tsx';
import { Users } from './pages/users/users.page.tsx';

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
                        path: ApplicationPaths.People,
                        children: [
                            {
                                element: <Users />,
                                index: true,
                            },
                            {
                                path: ApplicationPaths.User,
                                element: <User />,
                            },
                        ],
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
                    {
                        path: ApplicationPaths.PlatformsConfigs,
                        element: <ProtectedRoute />,
                        children: [
                            {
                                index: true,
                                element: <PlatformsConfigs />,
                            },
                            {
                                path: ApplicationPaths.PlatformServiceConfig,
                                element: <PlatformServiceConfig />,
                            },
                            {
                                path: ApplicationPaths.PlatformServiceConfigNew,
                                element: <PlatformServiceConfigCreate />,
                            },
                        ],
                    },

                    {
                        path: ApplicationPaths.Environments,
                        element: <ProtectedRoute />,
                        children: [
                            {
                                index: true,
                                element: <Environments />,
                            },
                            {
                                path: ApplicationPaths.EnvironmentNew,
                                element: <EnvironmentCreate />,
                            },
                            {
                                path: ApplicationPaths.EnvironmentConfigs,
                                element: <EnvironmentConfigs />,
                            },
                            {
                                path: ApplicationPaths.EnvironmentConfigNew,
                                element: <EnvironmentConfigCreate />,
                            },
                            {
                                path: ApplicationPaths.EnvironmentConfig,
                                element: <EnvironmentConfig />,
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
