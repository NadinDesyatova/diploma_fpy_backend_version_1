import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; 
import { OneUser } from "./OneUser";


function AdminIsNotAuthorized () {
  return <h1>Не удалось получить список пользователей. Права администратора не подтверждены.</h1>
}

function AdminIsAuthorized ({state}) {
  const [viewUsers, setViewUsers] = useState([]);
  const [lastUsersUpload, setLastUsersUpload] = useState(new Date());
  const navigate = useNavigate();
  const { admin } = state;

  async function sendFetchToGetUsers (admin) {
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}get_users/`, { 
        method: 'POST',
        credentials: 'include', 
        mode: 'cors',
        body: JSON.stringify({request_from_admin: admin}),
        headers: { 
          'Content-Type': 'application/json',
        }
      });
      if (response.status === 200) {
        const responseJson = await response.json();
        console.log(responseJson);
        console.log("Пользователи успешно загружены");
        setViewUsers(responseJson);
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('Ошибка:', error.message);
    }
  }

  useEffect(() => {
    sendFetchToGetUsers(admin);
  }, [lastUsersUpload]);

  const uploadUsers = () => {
    setLastUsersUpload(new Date());
  };

  return (
    <div className="admin-content">
      <button onClick={uploadUsers}>Обновить список пользователей</button>
      <h2>Список пользователей:</h2>
      <ul className="users-list">
        {viewUsers.map((elem, i) => {
          return <OneUser key={i} adminState={state} elem={elem} navigate={navigate} setLastUsersUpload={setLastUsersUpload} />
        })}
      </ul>
    </div>
  )
}

export function UsersListForAdmin ({state}) {
  const { admin } = state || {};
  return (
    <>
      {admin 
        ? <AdminIsAuthorized state={state} /> 
        : <AdminIsNotAuthorized />}
    </>
  )
}
