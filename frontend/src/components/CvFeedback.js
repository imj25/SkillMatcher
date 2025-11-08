import React, { useState } from 'react';

function CvFeedback() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('access');

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    if (!file) {
      setStatus("❌ Please upload a PDF resume.");
      return;
    }
  
    console.log("File selected:", file);  // Log file object directly
  
    const formData = new FormData();
    formData.append('cv_file', file); // Ensure this is correct
  
    // Check FormData contents by using FormData.entries() to log each key-value pair
    for (let entry of formData.entries()) {
      console.log(entry); // This will log each pair of [key, value]
    }
  
    setLoading(true);
    setStatus("⏳ Generating feedback...");
    setFeedback("");
  
    try {
      const response = await fetch('http://127.0.0.1:8000/api/cv-feedback/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });
  
      const data = await response.json();
      console.log("Backend response:", data);  // Log backend response for debugging
  
      if (response.ok) {
        setFeedback(data.feedback || '✅ Feedback received!');
        setStatus('');
      } else {
        setStatus("❌ Error: " + (data.error || JSON.stringify(data)));
      }
    } catch (error) {
      setStatus("❌ Something went wrong: " + error.message);
    }
  
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 text-dark font-sans py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-md space-y-6">
        <h2 className="text-3xl font-bold text-primary text-center">📄 Get CV Feedback</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full border border-gray-300 px-4 py-2 rounded"
            required
          />
          <button
            type="submit"
            className="bg-primary text-white px-6 py-2 rounded hover:bg-orange-500 transition"
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Get Feedback'}
          </button>
          {status && <p className="text-sm mt-2 text-gray-700">{status}</p>}
        </form>

        {feedback && (
          <div className="bg-gray-50 border border-gray-300 rounded-lg p-4 mt-4">
            <h3 className="text-lg font-semibold text-primary mb-2">🧠 Feedback</h3>
            <p className="whitespace-pre-line text-gray-700">{feedback}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default CvFeedback;

