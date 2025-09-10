import './App.css';
import { Routes, Route, BrowserRouter } from "react-router-dom";
import MainHeader from './ui/main-header/MainHeader';
import { StartPage } from './ui/start-page/StartPage';
import { MyCloud } from './ui/my-cloud/MyCloud';
import { MyFiles } from './ui/files/MyFiles';
import { PageIsNotFound } from './ui/user-auth-error/PageIsNotFound';
import { AdminPage } from './ui/admin/AdminPage';
import { UserFilesForAdmin } from './ui/admin/UserFilesForAdmin';
import { ShareFilePage } from './ui/share-file-page/ShareFilePage';

function App() {

  return (
    <div className="main-container">
      <MainHeader />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<StartPage />} />
          <Route path="/mycloud" element={<MyCloud />} />
          <Route path="/mycloud/admin" element={<AdminPage />} />
          <Route path="/mycloud/admin/user/:user_id/files" element={<UserFilesForAdmin />} />
          <Route path="/mycloud/my-files" element={<MyFiles />} />
          <Route path="/mycloud/page-not-found" element={<PageIsNotFound />} />
          <Route path="/share/:fileLink" element={<ShareFilePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
