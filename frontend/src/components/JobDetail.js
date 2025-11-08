import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [cv, setCv] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/jobs/list/`)
      .then(res => res.json())
      .then(data => {
        const selected = data.find(job => job.id === parseInt(id));
        setJob(selected);
      });
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!cv) {
      setStatus("❌ Please select a CV file.");
      return;
    }

    setLoading(true);
    setStatus("⏳ Submitting your application...");

    const formData = new FormData();
    formData.append('job', id);
    formData.append('cv_file', cv);

    const token = localStorage.getItem('access');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/apply/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setStatus("✅ Application submitted successfully!");
      } else {
        setStatus("❌ Submission failed: " + (data.error || JSON.stringify(data)));
      }
    } catch (err) {
      setStatus("❌ Error occurred: " + err.message);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 text-dark font-sans py-12 px-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-xl shadow-md space-y-8">
        {!job ? (
          <p>Loading job details...</p>
        ) : (
          <>
            <div>
              <h2 className="text-3xl font-bold text-primary mb-2">{job.title}</h2>
              <p className="text-sm text-gray-500 mb-4">📍 {job.location}</p>
              <p className="text-gray-700">{job.description}</p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-4">📤 Apply to this job</h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <input
                  type="file"
                  onChange={(e) => setCv(e.target.files[0])}
                  accept=".pdf"
                  className="block w-full border border-gray-300 rounded px-4 py-2"
                  required
                />
                <button
                  type="submit"
                  className="bg-primary text-white px-6 py-2 rounded hover:bg-orange-500 transition"
                  disabled={loading}
                >
                  {loading ? 'Submitting...' : 'Submit Application'}
                </button>
              </form>
              {status && <p className="mt-4 text-sm">{status}</p>}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default JobDetail;

