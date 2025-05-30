import { Navigate, Outlet } from 'react-router';

import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths } from '@/types/navigation';

const ProtectedRoute = () => {
    const { data: access } = useCheckAccessQuery({
        action: AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION,
    });
    const canAccess = access?.allowed ?? false;
    return canAccess ? <Outlet /> : <Navigate to={ApplicationPaths.Home} replace />;
};

export default ProtectedRoute;
