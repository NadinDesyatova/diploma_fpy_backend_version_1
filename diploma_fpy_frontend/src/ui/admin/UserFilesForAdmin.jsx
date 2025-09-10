import { useLocation, useNavigate } from 'react-router-dom';
import { ViewFilesStorage } from '../files/ViewFilesStorage';

export function UserFilesForAdmin () {
  const location = useLocation();
  const { userId, userName, adminState } = location.state || {};
  const navigate = useNavigate();
    
  const onClickBackButton = () => {
    navigate("/mycloud/admin", { state: adminState, replace: false });
  };

  return (
    <div className='container'>
      <button onClick={onClickBackButton}>Назад</button>
      <h2>Файлы пользователя {userName}</h2>
      <ViewFilesStorage id={userId} isUserFilesForAdmin={adminState["admin"]} />
    </div>
  );
}
