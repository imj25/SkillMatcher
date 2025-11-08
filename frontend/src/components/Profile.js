import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Profile() {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const token = localStorage.getItem('access');
  const userType = localStorage.getItem('user_type');
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchProfileData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/profile/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        const data = await response.json();
        if (response.ok) {
          setUserData(data);
        } else {
          setError(data.error || 'Failed to load profile');
        }
      } catch (error) {
        setError('An error occurred while fetching the profile.');
        console.error('Error fetching profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, [token, navigate]);

  if (loading) return <p className="text-center mt-8">Loading...</p>;
  if (error) return <p className="text-red-600 text-center mt-8">{error}</p>;

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="max-w-3xl mx-auto bg-white shadow-md rounded-lg p-8">
        <h2 className="text-2xl font-bold text-primary mb-4 text-center">👤 My Profile</h2>

        <p className="mb-2"><strong>Username:</strong> {userData.name}</p>
        <p className="mb-6"><strong>Email:</strong> {userData.email}</p>

        {userType === 'job_seeker' && (
          <>
            <h3 className="text-lg font-semibold mb-2">📋 Jobs You Applied To:</h3>
            {userData.applied_jobs && userData.applied_jobs.length > 0 ? (
            <div className="overflow-x-auto rounded-lg shadow">
                <table className="min-w-full border border-gray-300 bg-white text-sm text-gray-800">
                <thead className="bg-orange-500 text-white">
                    <tr>
                    <th className="px-6 py-3 text-left font-semibold">Job Title</th>
                    <th className="px-6 py-3 text-left font-semibold">Company</th>
                    </tr>
                </thead>
                <tbody>
                    {userData.applied_jobs.map((job, index) => (
                    <tr
                        key={index}
                        className={index % 2 === 0 ? "bg-gray-50" : "bg-gray-100"}
                    >
                        <td className="px-6 py-3 border-t border-gray-300">{job.title}</td>
                        <td className="px-6 py-3 border-t border-gray-300">{job.company}</td>
                    </tr>
                    ))}
                </tbody>
                </table>
            </div>
            ) : (
            <p className="text-gray-500">You haven't applied to any jobs yet.</p>
            )}

          </>
        )}

        {userType === 'company' && (
          <>
            <h3 className="text-lg font-semibold mt-6 mb-2">📢 Jobs You've Posted:</h3>
            <ul className="list-disc pl-5 space-y-2">
              {userData.posted_jobs && userData.posted_jobs.length > 0 ? (
                userData.posted_jobs.map((job, index) => (
                  <li key={index} className="text-gray-800">{job.title}</li>
                ))
              ) : (
                <li className="text-gray-500">No jobs posted yet.</li>
              )}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}

export default Profile;

