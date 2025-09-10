import { useState } from 'react';
import DownloadButton from './DownloadButton';
import { formatDate } from '../../common/formatDate';


export function OneFile ({userId, isUserFilesForAdmin, fileLink, elem, setLastFileUpload}) {
  const [currentFileLink, setCurrentFileLink] = useState(fileLink);
  const [errorMsg, setErrorMsg] = useState("");
  
  const onGetLink = async (fileId) => {
    console.log("Получение ссылки на файл");
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}get_link_for_file/`, {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({file_id: fileId})
      });

      if (response.status === 200) {
        const responseJson = await response.json();
        if (responseJson.status_code === 200) {
          setErrorMsg("");
          setCurrentFileLink(`${import.meta.env.VITE_APP_BASE_URL_WEBSITE}share/${responseJson.file_link}`);          
          console.log(responseJson);
        } else {
          setErrorMsg(`Не удалось получить ссылку, ошибка: ${responseJson.error_message}`);
        }      
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {
      setErrorMsg(`Не удалось получить ссылку, ошибка: ${error.message}`);
    }
  }

  const onDelete = async (id) => {
    console.log("Удаление файла");
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}files/${id}/`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.status === 204) {
        console.log(response);
        setErrorMsg("");
        setLastFileUpload(new Date());        
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }
    } catch (error) {
      setErrorMsg(`При удалении возникла ошибка: ${error.message}`);
    }
  }
  
  const changeFile = async (elemId, changingField, promtMsg) => {
    const newValue = prompt(`Введите ${promtMsg}: `);

    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}files/${elemId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        mode: 'cors',
        body: JSON.stringify({
          changing_field: changingField,
          new_value: newValue
        })
      });
      if (response.status === 200) {
        const responseJson = await response.json();
        if (responseJson.status_code === 200) {
          console.log(responseJson);
          setErrorMsg("");
          setLastFileUpload(new Date());
        } else {
          setErrorMsg(`Не удалось изменить файл: ${responseJson.error_message}`);
        }
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);        
      }      
    } catch (error) {
      setErrorMsg(`Не удалось изменить файл, возникла ошибка: ${error.message}`);
    }
  }

  return ( 
    <li className="one-file" id={elem.id} key={elem.id}>
      <h3>{elem.file_name}</h3>      
      <span>{`${parseFloat(parseInt(elem.file_size) / 1000000)} MB`}</span>
      <span>{formatDate(elem.date)}</span>
      <div className="buttons-block">
        <button onClick={() => {changeFile(elem.id, "file_name", "новое имя файла с расширением")}}>Переименовать</button>
        <button onClick={() => {changeFile(elem.id, "comment", "новый комментарий")}}>Изменить комментарий</button>
        <DownloadButton userId={userId} isUserFilesForAdmin={isUserFilesForAdmin} fileData={elem} setLastFileUpload={setLastFileUpload} />
      </div> 
      <span>Последняя дата скачивания: {elem.last_upload_date !== null ? formatDate(elem.last_upload_date) : ""}</span><br />
      <div>Комментарий к файлу: {elem.comment}</div>
      <span>Ссылка на файл (если ссылка не отображается, нажмите на кнопку "Поделиться файлом"): </span>
      <a href={currentFileLink}>{currentFileLink ? "Действующая ссылка" : ""}</a>
      <div className="buttons-block">
        <button onClick={() => onGetLink(elem.id)}>Поделиться файлом</button>
        <button onClick={() => onDelete(elem.id)}>Удалить файл</button>
      </div>
      <div className="error-msg">{errorMsg}</div>      
    </li>
  );
};
