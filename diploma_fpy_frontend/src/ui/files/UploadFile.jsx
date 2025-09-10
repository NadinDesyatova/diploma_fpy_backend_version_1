import { useState } from 'react';


function UploadFile ({ userId, setLastFileUpload}) {
  const [inputContent, setInputContent] = useState({
    'new_file': null,
    'file_name': '',
    'comment': ''
  })
  
  const [resultMsg, setResultMsg] = useState('');
  const serverUrl = `${import.meta.env.VITE_APP_BASE_USL_API}files/`;

  const onChangeHandler = (e) => {
    setResultMsg('');
    const { name, value } = e.target;
    console.log(e.target.files);
    setInputContent((prev) => ({
      ...prev, 
      [name]: name === 'new_file' ? e.target.files[0] : value
    }));
  };

  async function sendFileFetch (serverUrl, formData) {
    try {
      console.log('Происходит отправка файла на сервер');
      const response = await fetch(serverUrl, {
        method: 'POST',
        credentials: 'include',
        mode: 'cors',
        body: formData
      });

      if (response.status === 200) {
        await response.json();
        setResultMsg('Файл успешно загружен');
        setTimeout(() => {
          setResultMsg('');
          setInputContent({
            'new_file': null,
            'file_name': '',
            'comment': ''
          });
          setLastFileUpload(new Date());
        }, 100);
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);        
      }
    } catch (error) {
      setResultMsg(`Возникла ошибка: ${error.message}`);
    }
  }

  const uploadHandler = () => {
    if (inputContent.new_file === null) {
      alert('Пожалуйста, выберите файл для загрузки.');
      return;
    }

    const formData = new FormData();

    for (const [name, value] of Object.entries(inputContent)) {
      formData.append(name, value) 
    };

    const originalName = inputContent.new_file.name;

    let extension = "";

    const dotIndex = originalName.indexOf('.'); 
    if (dotIndex !== -1) {
      extension = originalName.substring(dotIndex);
    }

    formData.append('extension', extension);

    formData.append('file_size', inputContent.new_file.size);
  
    formData.append('user_id', userId);
    
    sendFileFetch(serverUrl, formData);   
  };

  return (
    <div className="upload-form">
      <h2>Добавить новый файл:</h2>
      <div className="input-block">
        <input type="file" name="new_file" onChange={onChangeHandler} placeholder="Загрузка файла" className="input-form" required />
        <input type="text" name="file_name" value={inputContent.file_name} onChange={onChangeHandler} placeholder="Имя файла с расширением" className="input-form" required />
        <input type="textarea" name="comment" value={inputContent.comment} onChange={onChangeHandler} placeholder="Комментарий" className="input-form" required />
        <div className="result-msg">{resultMsg}</div>
      </div>
      <div className="buttons-block">
        <button onClick={uploadHandler} className="button-form submit">Загрузить</button>
      </div>
    </div>
  );
};

export default UploadFile;
