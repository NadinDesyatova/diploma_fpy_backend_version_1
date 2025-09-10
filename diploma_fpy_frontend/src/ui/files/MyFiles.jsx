import { useLocation } from 'react-router';
import { ViewFilesStorage } from './ViewFilesStorage';
import { MyCloudContent } from '../my-cloud/MyCloudContent';


export function MyFiles () {    
  const location = useLocation();
  const { id, name, login } = location.state || {};

  return (
    <MyCloudContent name={name} login={login}>
      <ViewFilesStorage id={id} isUserFilesForAdmin={false} />
    </MyCloudContent>
  );
}