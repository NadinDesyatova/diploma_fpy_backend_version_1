import { useState } from "react";
import {Authorization} from "./Authorization";
import { Registration } from "./Registration";


export function StartPage () {

  const [viewPage, SetViewPage] = useState('Authorization');

  return (
    <>  
      {viewPage === "Authorization" 
        ? <Authorization SetViewPage={SetViewPage} /> 
        : <Registration SetViewPage={SetViewPage} />}
    </>    
  );
}
