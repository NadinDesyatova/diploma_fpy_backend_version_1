export function formatDate(dateString) {
   
  const date = new Date(dateString);

  const months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"];

  const hours = String(date.getHours()).padStart(2, '0'); 
  const minutes = String(date.getMinutes()).padStart(2, '0'); 
  const day = String(date.getDate()).padStart(2, '0');
  const month = months[date.getMonth()]; 
  const year = date.getFullYear(); 

  return `${hours}:${minutes} ${day} ${month} ${year}`;
}
