import { useState } from "react";

export function Registration ({ SetViewPage }) {
  const [inputInfo, setInputInfo] = useState({
    name: '',
    login: '',
    password: '',
    email: ''
  });
  
  const [resultMsg, setResultMsg] = useState('');

  const inputRequirements = {
    login: {
      regex: "^[a-zA-Z]{1}[a-zA-Z0-9]{3,20}$",
      titleText: "Вводите только латинские буквы и цифры, первый символ - буква, длина от 4 до 20 символов."
    },
    password: {
      regex: "^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\\W).{6,}$",
      titleText: "Введите не менее 6 символов: по крайней мере, одну заглавную букву, одну цифру и один специальный символ."
    },
    email: {
      regex: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
      titleText: "Введите правильный адрес электронной почты."
    }
  };

  const onChange = (e) => {
    setResultMsg('');
    const { name, value } = e.target;
    setInputInfo((prev) => ({
      ...prev, 
      [name]: value
    }))
  };

  async function sendFetchForRegistration () {
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}users/`, {
        method: "POST",
        body: JSON.stringify(inputInfo),
        headers: {
          "Content-Type": "application/json",
        }
      });
      if (response.status === 200) {
        const responseJson = await response.json();
        console.log(responseJson);
        if (responseJson.status_code === 200) {
          setResultMsg("Успешно создан аккаунт. Нажмите, пожалуйста, на кнопку 'Войти' для перехода на страницу входа.")
        } else {
          setResultMsg(responseJson.error_message);
        }
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }      
    } catch (error) {
      setResultMsg(`Ошибка: ${error.message}`);
    }
  }

  const onSubmit = (e) => {
    e.preventDefault();
    sendFetchForRegistration();    
  };

  return (
    <div className="container-form">
      <form onSubmit={onSubmit} className="auth-form">
        <h2>Регистрация</h2>
        <div className="input-block">
          <input type="text" name="name" onChange={onChange} placeholder="Имя" className="input-form" required />
          <input type="text" name="login" onChange={onChange} placeholder="Логин" title={inputRequirements.login.titleText} className="input-form" required pattern={inputRequirements.login.regex} />
          <input type="password" name="password" onChange={onChange} placeholder="Пароль" title={inputRequirements.password.titleText} className="input-form" required pattern={inputRequirements.password.regex} />
          <input type="email" name="email" onChange={onChange} placeholder="email" title={inputRequirements.email.titleText} className="input-form" required pattern={inputRequirements.email.login} />
          <div className="result-msg">{resultMsg}</div>
        </div>
        <div className="buttons-block">
          <button type="submit" className="button-form submit">Зарегестрироваться</button>
          <button onClick={() => {SetViewPage("Authorization")}} className="button-form">Войти</button>
        </div>
      </form>
    </div>
  );
}
