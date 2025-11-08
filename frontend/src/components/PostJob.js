import React, { useState } from 'react';

function PostJob() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [status, setStatus] = useState('');
  const token = localStorage.getItem('access');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch('http://127.0.0.1:8000/api/jobs/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ title, description, location })
    });

    const data = await response.json();

    if (response.ok) {
      setStatus('✅ Job posted successfully!');
      setTitle('');
      setDescription('');
      setLocation('');
    } else {
      setStatus('❌ Failed to post job: ' + (data.error || JSON.stringify(data)));
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-dark font-sans py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-md space-y-6">
        <h2 className="text-3xl font-bold text-primary text-center">📝 Post a Job</h2>

        {status && (
          <div className="text-center text-sm">
            <p className={status.startsWith('✅') ? 'text-green-600' : 'text-red-500'}>{status}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">📌 Job Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full border border-gray-300 px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">📍 Location</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full border border-gray-300 px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">📝 Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border border-gray-300 px-4 py-2 rounded h-32 resize-none focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
          </div>

          <button
            type="submit"
            className="bg-primary text-white px-6 py-2 rounded hover:bg-orange-500 transition"
          >
            ➕ Post Job
          </button>
        </form>
      </div>
    </div>
  );
}

export default PostJob;
