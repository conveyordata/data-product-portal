import { useSelector } from 'react-redux';
import { Navigate, Outlet } from 'react-router';

import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { ApplicationPaths } from '@/types/navigation';

const ProtectedRoute = () => {
    const currentUser = useSelector(selectCurrentUser);
    const { data: access } = useCheckAccessQuery({
        action: AuthorizationAction.GLOBAL_UPDATE_CONFIGURATION,
    });
    const canAccess = access?.access || false;
    return currentUser?.is_admin || canAccess ? <Outlet /> : <Navigate to={ApplicationPaths.Home} replace />;
};

export default ProtectedRoute;
