import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import DownloadShareFile from './DownloadShareFile';

export function ShareFilePage () {
  const { fileLink } = useParams();
  const [fileData, setFileData] = useState('');
  console.log(fileLink);
  
  const sendFetchForShareFile = async (url) => {
    try {
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include'
      });
      
      if (response.status === 200) {
        const responseJson = await response.json();
        console.log(responseJson);
        setFileData(responseJson);
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('Ошибка:', error.message);
      alert("К сожалению, возникла ошибка, попробуйте зайти на сайт позже");  
    }
  }

  useEffect(() => {
    if (fileLink !== undefined) {
      const url = `${import.meta.env.VITE_APP_BASE_USL_API}retrieve_by_link/?link=${fileLink}`;
      sendFetchForShareFile(url);
    }
  }, [fileLink]);
  

  return (
    <div className='container'>
      <h1>С Вами поделились файлом: {fileData.file_name}</h1>
      <DownloadShareFile fileId={fileData.id} userId={fileData.user_id} fileName={fileData.file_name} />
    </div>
  );
};
