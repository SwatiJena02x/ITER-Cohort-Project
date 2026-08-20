import { useEffect, useState } from 'react'
import './App.css'

const API_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedSession, setSelectedSession] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState('')
  const [uploadError, setUploadError] = useState('')

  const [query, setQuery] = useState('')
  const [investigating, setInvestigating] = useState(false)
  const [investigationResult, setInvestigationResult] = useState('')
  const [investigationError, setInvestigationError] = useState('')

  useEffect(() => {
    fetch(`${API_URL}/sessions`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch sessions')
        }

        return response.json()
      })
      .then((data) => {
        setSessions(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0] || null)
    setUploadResult('')
    setUploadError('')
  }

  const handleUpload = async () => {
    if (!selectedSession) {
      setUploadError('Please select an exam session.')
      return
    }

    if (!selectedFile) {
      setUploadError('Please select an image.')
      return
    }

    setUploading(true)
    setUploadResult('')
    setUploadError('')

    const formData = new FormData()

    formData.append('session_id', selectedSession)
    formData.append('file', selectedFile)

    try {
      const response = await fetch(
        `${API_URL}/upload-evidence`,
        {
          method: 'POST',
          body: formData,
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Evidence upload failed.'
        )
      }

      setUploadResult(
        `Evidence uploaded successfully: ${data.evidence_id}`
      )

      setSelectedFile(null)

    } catch (err) {
      setUploadError(err.message)

    } finally {
      setUploading(false)
    }
  }

  const handleInvestigation = async () => {
    if (!query.trim()) {
      setInvestigationError(
        'Please enter an investigation question.'
      )
      return
    }

    setInvestigating(true)
    setInvestigationResult('')
    setInvestigationError('')

    try {
      const response = await fetch(
        `${API_URL}/investigate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: query.trim(),
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Investigation failed.'
        )
      }

      setInvestigationResult(data.answer)

    } catch (err) {
      setInvestigationError(err.message)

    } finally {
      setInvestigating(false)
    }
  }

  return (
    <div className="app">

      {/* Header */}

      <header className="header">

        <div className="brand">
          <div className="brand-icon">
            VV
          </div>

          <div>
            <h1>VectorVanguard</h1>

            <p>
              Offline AI Evidence Investigation System
            </p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Local AI System
        </div>

      </header>


      {/* Main */}

      <main className="dashboard">

        <section className="welcome">

          <div>
            <span className="eyebrow">
              OFFLINE INTELLIGENCE
            </span>

            <h2>
              Evidence Investigation
            </h2>

            <p>
              Upload exam evidence and investigate it
              using the local AI pipeline.
            </p>
          </div>

        </section>


        <section className="cards">

          {/* Evidence Upload */}

          <div className="card">

            <div className="card-icon">
              ↑
            </div>

            <h3>
              Evidence Upload
            </h3>

            <p className="card-description">
              Upload CCTV snapshots or exam-environment
              images for local AI processing.
            </p>

            <label>
              Exam Session
            </label>

            <select
              value={selectedSession}
              onChange={(event) =>
                setSelectedSession(event.target.value)
              }
            >
              <option value="">
                Select a session
              </option>

              {sessions.map((session) => (
                <option
                  key={session.id}
                  value={session.id}
                >
                  {session.exam_name}
                  {' '}
                  (Session {session.id})
                </option>
              ))}
            </select>


            <label>
              Evidence Image
            </label>

            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
            />

            {selectedFile && (
              <div className="file-preview">
                <span>Selected:</span>
                <strong>
                  {selectedFile.name}
                </strong>
              </div>
            )}


            <button
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading
                ? 'Processing...'
                : 'Upload Evidence'}
            </button>


            {uploadResult && (
              <div className="success-message">
                ✓ {uploadResult}
              </div>
            )}

            {uploadError && (
              <div className="error-message">
                Error: {uploadError}
              </div>
            )}

          </div>


          {/* Investigation */}

          <div className="card investigation-card">

            <div className="card-icon">
              ?
            </div>

            <h3>
              Investigation
            </h3>

            <p className="card-description">
              Ask questions about processed evidence
              using the local RAG system.
            </p>

            <label>
              Investigation Question
            </label>

            <textarea
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="Example: Was a mobile phone visible near the student's desk?"
              rows="4"
            />


            <button
              onClick={handleInvestigation}
              disabled={investigating}
            >
              {investigating
                ? 'Investigating...'
                : 'Investigate Evidence'}
            </button>


            {investigationResult && (
              <div className="result">

                <div className="result-header">

                  <div>
                    <span className="result-label">
                      INVESTIGATION RESULT
                    </span>

                    <strong>
                      AI Answer
                    </strong>
                  </div>

                  <span className="result-status">
                    Evidence Grounded
                  </span>

                </div>

                <div className="result-answer">
                  {investigationResult}
                </div>

              </div>
            )}


            {investigationError && (
              <div className="error-message">
                Error: {investigationError}
              </div>
            )}

          </div>


          {/* Exam Sessions */}

          <div className="card">

            <div className="card-icon">
              ◉
            </div>

            <h3>
              Exam Sessions
            </h3>

            <p className="card-description">
              Sessions currently available in PostgreSQL.
            </p>


            {loading && (
              <div className="loading">
                Loading sessions...
              </div>
            )}


            {error && (
              <div className="error-message">
                Error: {error}
              </div>
            )}


            {!loading && !error && (
              <div className="session-list">

                {sessions.length === 0 ? (
                  <p>
                    No exam sessions found.
                  </p>
                ) : (
                  sessions.map((session) => (
                    <div
                      className="session-item"
                      key={session.id}
                    >

                      <div className="session-main">
                        <strong>
                          {session.exam_name}
                        </strong>

                        <span>
                          Session {session.id}
                        </span>
                      </div>

                      <div className="session-meta">
                        Student ID: {session.student_id}
                      </div>

                    </div>
                  ))
                )}

              </div>
            )}

          </div>

        </section>

      </main>


      {/* Footer */}

      <footer className="footer">
        <span>
          VectorVanguard
        </span>

        <span>
          Offline • Private • Evidence-Grounded
        </span>
      </footer>

    </div>
  )
}

export default App