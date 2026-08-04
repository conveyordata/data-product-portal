import { NuqsAdapter } from 'nuqs/adapters/react-router/v7';
import { createBrowserRouter, Navigate, RouterProvider, useParams } from 'react-router';
import { AuthLayout } from '@/components/layout/auth/auth.layout.tsx';
import PublicLayout from '@/components/layout/public/public.layout.tsx';
import RootLayout from '@/components/layout/root/root.layout.tsx';
import { Logout } from '@/pages/auth/logout/logout-page.tsx';
import Cart from '@/pages/cart/cart.page.tsx';
import { DataProduct } from '@/pages/data-product/data-product.page.tsx';
import { DataProductCreate } from '@/pages/data-product-create/data-product-create.page.tsx';
import { DataProductEdit } from '@/pages/data-product-edit/data-product-edit.page.tsx';
import { Dataset } from '@/pages/dataset/dataset.page.tsx';
import { DatasetEdit } from '@/pages/dataset-edit/dataset-edit.page.tsx';
import { ErrorRootElement } from '@/pages/error/error-root-element.page.tsx';
import { ExplorationPage } from '@/pages/exploration/exploration.page.tsx';
import { ExplorationEdit } from '@/pages/exploration-edit/exploration-edit.page.tsx';
import { ExplorerPage } from '@/pages/explorer/explorer.page.tsx';
import { Home } from '@/pages/home/home.page.tsx';
import { Marketplace } from '@/pages/marketplace/marketplace.page.tsx';
import { PeoplePage } from '@/pages/people/people-table.component.tsx';
import { ProductStudio } from '@/pages/product-studio/product-studio.page.tsx';
import { ApplicationPaths } from '@/types/navigation';
import ProtectedRoute from './components/layout/protected/protected.layout.tsx';
import { Settings } from './pages/settings/settings.page.tsx';
import { TechnicalAsset } from './pages/technical-asset/technical-asset.page.tsx';
import { TechnicalAssetEdit } from './pages/technical-asset-edit/technical-asset-edit.page.tsx';

function DataProductsRedirect() {
    const params = useParams();
    const splatPath = params['*'] || '';
    return <Navigate to={`/studio/${splatPath}`} replace />;
}

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
                        path: ApplicationPaths.Studio,
                        children: [
                            {
                                element: <ProductStudio />,
                                index: true,
                            },
                            {
                                path: ApplicationPaths.DataProduct,
                                element: <DataProduct />,
                            },
                            {
                                path: ApplicationPaths.Exploration,
                                element: <ExplorationPage />,
                            },
                            {
                                path: ApplicationPaths.ExplorationEdit,
                                element: <ExplorationEdit />,
                            },
                            {
                                path: ApplicationPaths.DataOutput,
                                element: <TechnicalAsset />,
                            },
                            {
                                path: ApplicationPaths.DataOutputEdit,
                                element: <TechnicalAssetEdit />,
                            },
                            {
                                path: ApplicationPaths.DataProductNew,
                                element: <DataProductCreate />,
                            },
                            {
                                path: ApplicationPaths.DataProductEdit,
                                element: <DataProductEdit />,
                            },
                            {
                                path: ApplicationPaths.OutputPort,
                                element: <Dataset />,
                            },
                            {
                                path: ApplicationPaths.OutputPortEdit,
                                element: <DatasetEdit />,
                            },
                        ],
                    },
                    {
                        path: `${ApplicationPaths.DataProducts}/*`,
                        element: <DataProductsRedirect />,
                    },
                    {
                        path: ApplicationPaths.Marketplace,
                        element: <Navigate to={ApplicationPaths.Marketplace} />,
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
                        path: ApplicationPaths.Marketplace,
                        children: [
                            {
                                element: <Marketplace />,
                                index: true,
                            },

                            {
                                path: ApplicationPaths.MarketPlaceOutputPort,
                                element: <Dataset />,
                            },
                            {
                                path: ApplicationPaths.MarketPlaceOutputPortEdit,
                                element: <DatasetEdit />,
                            },
                        ],
                    },
                    {
                        path: ApplicationPaths.People,
                        element: <PeoplePage />,
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
