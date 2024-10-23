import { Navigate, Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { ApplicationPaths } from '@/types/navigation';

const ProtectedRoute = () => {
    const currentUser = useSelector(selectCurrentUser);
    return currentUser?.is_admin ? <Outlet /> : <Navigate to={ApplicationPaths.Home} replace />;
};

export default ProtectedRoute;
