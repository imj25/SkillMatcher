import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    // Clear auth-related data
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_type');

    // Redirect to home
    navigate('/');
  }, [navigate]);

  return null;
}

export default Logout;
