import { useEffect, useState } from 'react';
import UploadFile from './UploadFile';
import { OneFile } from './OneFile';
import { sortByDate } from '../../common/sortingDate';
import { useNavigate } from 'react-router-dom';

export function ViewFilesStorage ({id, isUserFilesForAdmin}) {
  const [viewFiles, setViewFiles] = useState([]);
  const [lastFileUpload, setLastFileUpload] = useState(new Date());
  const navigate = useNavigate();

  async function sendFetchToGetUserFiles (id) {
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}get_user_files/`, { 
        method: 'POST',
        credentials: 'include', 
        mode: 'cors',
        body: JSON.stringify({
          user_id: id
        }),
        headers: { 
          'Content-Type': 'application/json',
        }
      }); 
      if (response.status === 200) {
        const responseJson = await response.json();
        if (responseJson) {
          setViewFiles(sortByDate(responseJson));
        }
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {       
      console.error('Ошибка при отправке запроса:', error.message);
      navigate('/mycloud/page-not-found', { replace: false });
    }
  }
  
  useEffect(() => {
    sendFetchToGetUserFiles(id);
  }, [lastFileUpload]);

  return (
    <div className="container">
      <button className="button-update-files" onClick={() => {setLastFileUpload(new Date())}}>Обновить список файлов</button>
      <UploadFile userId={id} setLastFileUpload={setLastFileUpload}/>
      <h3 className="files-list-tittle">Список файлов:</h3>
      <ul>
        {viewFiles.map((elem, i) => {
          const fileLink = 
            elem.file_link 
              ? `${import.meta.env.VITE_APP_BASE_URL_WEBSITE}share/${elem.file_link}` 
              : ""
          return <OneFile key={i} userId={id} isUserFilesForAdmin={isUserFilesForAdmin} fileLink={fileLink} elem={elem} setLastFileUpload={setLastFileUpload} />
        })}
      </ul>
    </div>
  );
}
