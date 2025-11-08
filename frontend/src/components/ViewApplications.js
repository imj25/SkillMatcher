import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const DJANGO_ORIGIN = 'http://127.0.0.1:8000';
const FASTAPI_ORIGIN = 'http://127.0.0.1:8001';

function ViewApplications() {
  const [jobs, setJobs] = useState([]);
  // ───── Option 1 persistence ────────────────────────────────
  const [rankings, setRankings] = useState(() => {
    try {
      const stored = localStorage.getItem('rankings');
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });
  // ───────────────────────────────────────────────────────────
  const [error, setError] = useState('');
  const token = localStorage.getItem('access');
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    fetch(`${DJANGO_ORIGIN}/api/company/applications/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(result => {
        if (Array.isArray(result)) setJobs(result);
        else setError(result.error || 'Unexpected error');
      })
      .catch(err => setError('Failed to fetch applications: ' + err.message));
  }, [token, navigate]);

  const handleRankApplicants = async (job) => {
    if (!job || !job.applications?.length) return alert('No applications to rank');

    try {
      const formData = new FormData();
      formData.append('job_id', job.id);

      for (const app of job.applications) {
        if (!app.cv_url || app.cv_url.trim() === '') {
          console.warn(`Skipping applicant ${app.applicant_username || app.id} because cv_url is empty or missing.`);
          continue;
        }

        let sourceUrl = app.cv_url;
        if (!sourceUrl.startsWith('http') && !sourceUrl.startsWith('/media/')) {
          sourceUrl = `/media/${sourceUrl}`;
        }
        if (!sourceUrl.startsWith('http')) {
          sourceUrl = `${DJANGO_ORIGIN}${sourceUrl}`;
        }

        const res = await fetch(sourceUrl);
        const blob = await res.blob();
        const name = sourceUrl.split('/').pop();
        formData.append('files', new File([blob], name, { type: 'application/pdf' }));
      }

      const uploadRes = await fetch(`${FASTAPI_ORIGIN}/upload-cvs`, { method: 'POST', body: formData });
      if (!uploadRes.ok) throw new Error('Upload failed');
      const { cv_paths } = await uploadRes.json();

      const matchRes = await fetch(`${FASTAPI_ORIGIN}/match-candidates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title:      job.title,
          job_description: job.description || '',
          cv_paths,
        }),
      });
      if (!matchRes.ok) throw new Error('Matching failed');
      const matchData = await matchRes.json();

      // ───── save to state *and* localStorage ────────────────
      setRankings(prev => {
        const updated = { ...prev, [job.id]: matchData.results };
        localStorage.setItem('rankings', JSON.stringify(updated));
        return updated;
      });
      // ───────────────────────────────────────────────────────

    } catch (err) {
      console.error(err);
      alert('❌  ' + err.message);
    }
  };

  const getRankForApp = (jobId, app) => {
    const list = rankings[jobId] || [];
    if (!list.length || !app.cv_url) return null;

    const cvFileName = app.cv_url.split('/').pop(); // extract filename only
    return list.find(r => {
      const pathFileName = r.cv_path?.split(/[\\/]/).pop(); // handles / or \
      return pathFileName && pathFileName === cvFileName;
    });
  };
  return (
    <div className="min-h-screen bg-lightbg text-dark p-8">
      <h2 className="text-3xl font-bold text-primary mb-8">📄 Applications to Your Jobs</h2>
      {error && <p className="text-red-500">❌ {error}</p>}

      {jobs.length === 0 && !error && <p>No applications found yet.</p>}

      {jobs.map((job) => (
        <div key={job.id} className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">🧩 {job.title}</h3>
            <button
              onClick={() => handleRankApplicants(job)}
              className="bg-green-600 text-white px-4 py-1 rounded hover:bg-green-700 transition"
            >
              🎯 Rank Applicants
            </button>
          </div>

          {job.applications.length === 0 ? (
            <p>No applicants yet.</p>
          ) : (
            <ul className="space-y-4">
              {job.applications.map(app => {
                let finalCvUrl = app.cv_url;
                if (finalCvUrl && !finalCvUrl.startsWith('http') && !finalCvUrl.startsWith('/media/')) {
                  finalCvUrl = `/media/${finalCvUrl}`;
                }
                if (finalCvUrl && !finalCvUrl.startsWith('http')) {
                  finalCvUrl = `${DJANGO_ORIGIN}${finalCvUrl}`;
                }

                // ⮕ NEW: get correct ranking by cv_path
                const rank = getRankForApp(job.id, app);

                return (
                  <li key={app.id} className="bg-gray-50 p-4 rounded shadow-sm">
                    <div className="flex justify-between items-center">
                      <div>
                        <div>👤 {app.applicant_username || 'Unknown'}</div>
                        <div>📧 {app.applicant_email || 'No email'}</div>
                      </div>

                      <div className="flex flex-col items-end space-y-2">
                        <div className="flex space-x-3">
                          {app.cv_url && (
                            <a
                              href={finalCvUrl}
                              target="_blank"
                              rel="noreferrer"
                              className="bg-indigo-500 text-white px-4 py-1 rounded hover:bg-indigo-600"
                            >
                              📄 View CV
                            </a>
                          )}
                          {app.applicant_email && (
                            <a
                              href={`mailto:${app.applicant_email}`}
                              className="bg-green-500 text-white px-4 py-1 rounded hover:bg-green-600"
                            >
                              ✉️ Email
                            </a>
                          )}
                        </div>

                        {/* New score display */}
                        {rank && (
                          <div className="flex flex-col items-end w-full mt-2">
                            {/* Display Score */}
                            <span className="text-sm font-semibold text-gray-700">
                              Score: {rank.relevance_score.toFixed(1)}%
                            </span>

                            {/* Progress Bar */}
                            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                              <div
                                className={`h-2 rounded-full ${
                                  rank.relevance_score > 90 ? 'bg-blue-500'
                                  : rank.relevance_score > 70 ? 'bg-green-500'
                                  : rank.relevance_score > 50 ? 'bg-orange-400'
                                                              : 'bg-red-500'
                                }`}
                                style={{ width: `${rank.relevance_score}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </li>
                );
              })}

            </ul>
          )}
        </div>
      ))}
    </div>
  );
}

export default ViewApplications;

