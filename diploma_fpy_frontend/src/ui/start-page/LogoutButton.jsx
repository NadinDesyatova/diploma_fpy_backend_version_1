import { useNavigate } from 'react-router-dom';


function LogoutButton ({ login }) {
  const navigate = useNavigate()
  const handleLogout = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}logout/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        mode: 'cors',
        body: JSON.stringify({login: login}),
      });

      if (response.status == 204) {
        localStorage.clear();
        navigate("/", { replace: false });
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('Ошибка:', error.message);
      alert("Возникла техническая ошибка, попробуйте зайти на сайт позже");      
    }          
  }


  return (
    <button className="logout-btn" onClick={handleLogout}>
      Выйти
    </button>
  );
};

export default LogoutButton;
