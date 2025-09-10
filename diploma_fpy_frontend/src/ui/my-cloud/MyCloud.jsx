import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { UserIsNotAuthorized } from "../user-auth-error/UserIsNotAuthorize";

function RequestSending() {
  return <div>...Отправляется запрос. Подождите, пожалуйста, немного.</div>
}

export function MyCloud () {
  const [sessionUser, setSessionUser] = useState({});

  async function sendFetchToGetExistUser () {
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}get_mycloud_user/`, { 
        method: 'GET',
        credentials: 'include', 
        mode: 'cors',
        headers: { 
          'Content-Type': 'application/json',
        }
      });
      if (response.status === 200) {
        const responseJson = await response.json();
        console.log(responseJson);
        setSessionUser(responseJson.user);
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {
      setSessionUser(null);
      console.error('Возникла ошибка:', error.message);
    }
  }    

  useEffect(() => {
    sendFetchToGetExistUser();
  }, []);

  return (
    <div className="container">
      {sessionUser !== null 
        ? sessionUser.id 
          ? sessionUser["admin"] === true 
            ? <Navigate to="/mycloud/admin" state={sessionUser} replace={false} /> 
            : <Navigate to="/mycloud/my-files" state={sessionUser} replace={false} /> 
          : <RequestSending />
        : <UserIsNotAuthorized />}
    </div>
  )
}
