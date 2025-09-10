function DownloadShareFile ({ fileId, userId, fileName }) {
  
  const handleDownload = async (fileId, userId, fileName) => {
    console.log("Отправка запроса на получение файла");  
    try {
      const response = await fetch(`${import.meta.env.VITE_APP_BASE_USL_API}download_file/`, {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user_id: userId, 
          file_id: fileId,
          is_user_files_for_admin: false
        })
      });
      if (response.status === 200) {
        console.log("Загрузка файла"); 
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.append(a); 
        a.click();    
        a.remove(); 
      } else {
        const errorMsg = await response.text();
        throw new Error(errorMsg);
      }              
    } catch (error) {
      alert(`Ошибка: ${error.message}`); 
    }
  };

  return (
    <button onClick={() => handleDownload(fileId, userId, fileName)}>
      Скачать файл
    </button>
  );
};

export default DownloadShareFile;