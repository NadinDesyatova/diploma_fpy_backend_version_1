import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; 


export function Authorization ({ SetViewPage }) {
  const [inputInfo, setInputInfo] = useState({
    login: "",
    password: ""
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [requestWithLocalStorageData, setRequestWithLocalStorageData] = useState("");

  const navigate = useNavigate();

  async function sendFetchToCheckSession (storedLogin, storedPassword) {
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}check_session/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: 'include',
        body: JSON.stringify({login: storedLogin, password: storedPassword})
      });
      if (response.status === 200) {
        const responseJson = await response.json();
        if (responseJson.status_code === 200) {
          console.log("Вы успешно авторизовались", responseJson);
          navigate('/mycloud', { replace: false});
        }
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }     
    } catch (error) {
      setErrorMsg(`Возникла ошибка: ${error.message}`);
    } finally {
      setRequestWithLocalStorageData("");
    }
  }

  useEffect(() => {
    const storedLogin = localStorage.getItem('userLogin');
    const storedPassword = localStorage.getItem('userPassword');
    console.log(storedLogin);
    if (storedLogin && storedPassword) {
      setInputInfo({
        login: storedLogin,
        password: storedPassword
      });
      setRequestWithLocalStorageData("Отправляем запрос, подождите, пожалуйста...");
      sendFetchToCheckSession (storedLogin, storedPassword);
    }
  }, []);

  const onChange = (e) => {
    setErrorMsg("");
    const { name, value } = e.target;
    setInputInfo((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  async function sendFetchToLogin () {
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}login/`, {
        method: "POST",
        body: JSON.stringify(inputInfo),
        headers: {
          "Content-Type": "application/json",
        },
        credentials: 'include',
        withCredentials: true
      });
      if (response.status === 200) {
        const responseJson = await response.json();
        console.log(responseJson);
        console.log("Вы успешно авторизовались");

        localStorage.setItem('userLogin', inputInfo.login);
        localStorage.setItem('userPassword', inputInfo.password);

        navigate('/mycloud', { replace: false }); 
      } else if (response.status === 404) {
        console.log(response);
        setErrorMsg("Неверный логин или пароль");
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {
      setErrorMsg(`Возникла ошибка: ${error.message}`);
    }
  } 

  const onSubmit = (e) => {
    e.preventDefault();
    sendFetchToLogin();
  };

  return (
    <div className="container-form">      
      <form onSubmit={onSubmit} className="auth-form">   
        <h2 className="head-form">Войти</h2>
        <div>{requestWithLocalStorageData}</div>  
        <div className="input-block">
          <input type="text" placeholder="Логин" name="login" value={inputInfo.login} onChange={onChange} className="input-form"/>
          <input type="password" placeholder="Пароль" name="password" value={inputInfo.password} onChange={onChange} className="input-form"/>
          <div>{errorMsg}</div>
        </div>
        <div className="buttons-block">
          <button type="submit" className="button-form submit">Войти</button>
          <button className="button--form" onClick={() => { SetViewPage("Registration") }}>Зарегестрироваться</button>
        </div>
      </form>
    </div>
  );
};
