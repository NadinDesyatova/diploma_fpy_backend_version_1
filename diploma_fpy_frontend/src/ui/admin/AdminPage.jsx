import { useLocation } from 'react-router';
import { MyCloudContent } from '../my-cloud/MyCloudContent';
import { UsersListForAdmin } from './UsersListForAdmin';
import { ViewFilesStorage } from '../files/ViewFilesStorage';
import { UserIsNotAuthorized } from '../user-auth-error/UserIsNotAuthorize';

export function AdminPage () {    
  const location = useLocation();
  const { id, admin, name, login } = location.state || {};

  return (
    <>
      {admin
        ? <MyCloudContent name={name} login={login}>      
            <UsersListForAdmin state={location.state}/>
            <ViewFilesStorage id={id} isUserFilesForAdmin={false} />
          </MyCloudContent>
        : <UserIsNotAuthorized />}
    </>
  );
}