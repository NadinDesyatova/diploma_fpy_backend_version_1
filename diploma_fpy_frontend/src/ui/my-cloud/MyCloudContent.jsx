import LogoutButton from '../start-page/LogoutButton';


export function MyCloudContent ({name, login, children}) {    
  return (
    <>
      <LogoutButton login={login} />
      <h1>Добро пожаловать, {name}!</h1>
      <div className="cloud-content">{children}</div>
    </>
  );
}