import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import JobList from './components/JobList';
import JobDetail from './components/JobDetail';
import Register from './components/Register';
import Login from './components/Login';
import CvFeedback from './components/CvFeedback';
import Logout from './components/Logout';
import PostJob from './components/PostJob';
import ViewApplications from './components/ViewApplications';
import Navbar from './components/Navbar';
import Profile from './components/Profile'; 

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/jobs" element={<JobList />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/cv-feedback" element={<CvFeedback />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/post-job" element={<PostJob />} />
        <Route path="/view-applications" element={<ViewApplications />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
}


export default App;
