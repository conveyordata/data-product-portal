import { Navigate, Outlet } from 'react-router';

import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths } from '@/types/navigation';

const ProtectedRoute = () => {
    const { data: access } = useCheckAccessQuery({
        action: AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION,
    });

    if (access === undefined) {
        // Don't navigate until the request has resolved
        return null;
    }

    return access.allowed ? <Outlet /> : <Navigate to={ApplicationPaths.Home} replace />;
};

export default ProtectedRoute;
