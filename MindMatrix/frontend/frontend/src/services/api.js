// ============================================================
// api.js
// DSA Coach AI - Frontend API Service
// ============================================================

import axios from 'axios'

// ============================================================
// BACKEND URL
// ============================================================
//
// LOCAL DEVELOPMENT:
// http://127.0.0.1:8000
//
// RENDER PRODUCTION:
// https://dsa-coach-backend.onrender.com
//
// You can override this using:
// VITE_API_BASE_URL
// ============================================================

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'https://dsa-coach-backend.onrender.com'


  
// ============================================================
// AXIOS CLIENT
// ============================================================

const client = axios.create({
  baseURL: BASE_URL,

  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },

  timeout: 120000,
})


// ============================================================
// ANALYZE DSA SOLUTION
// ============================================================
//
// POST:
// /feedback/analyze
//
// Backend:
// FastAPI
//    ↓
// LangGraph / AI Agents
//    ↓
// Code Review
//    ↓
// Complexity
//    ↓
// Optimization
//    ↓
// Interview
//    ↓
// Learning
//    ↓
// Supervisor
//    ↓
// Final Feedback
// ============================================================

export async function analyzeSolution(payload) {
  try {
    console.log('Sending solution to backend...')
    console.log('Backend:', BASE_URL)
    console.log('Payload:', payload)

    const response = await client.post(
      '/feedback/analyze',
      payload
    )

    console.log('Backend response:', response.data)

    // Most likely backend response
    if (response.data?.feedback) {
      return response.data.feedback
    }

    // Fallback if backend directly returns the result
    return response.data

  } catch (error) {

    console.error(
      'Analyze solution error:',
      error
    )

    throw error
  }
}


// ============================================================
// GENERATE AI HINT
// ============================================================
//
// POST:
// /feedback/hint
//
// Hint levels:
//
// 1 → Conceptual hint
// 2 → Algorithm / data structure direction
// 3 → Detailed approach
//
// The backend should avoid giving the complete solution.
// ============================================================

export async function getHint({
  problem,
  language = 'Python',
  code = '',
  approach = '',
  hintLevel = 1,
}) {

  try {

    const response = await client.post(
      '/feedback/hint',
      {
        problem,
        language,
        code,
        approach,
        hint_level: hintLevel,
      }
    )

    console.log(
      'Hint response:',
      response.data
    )

    return response.data

  } catch (error) {

    console.error(
      'Hint generation error:',
      error
    )

    throw error
  }
}


// ============================================================
// HEALTH CHECK
// ============================================================
//
// GET:
// /health
//
// Used to verify that the backend is alive.
// ============================================================

export async function checkHealth() {

  try {

    const response = await client.get(
      '/health'
    )

    console.log(
      'Backend health:',
      response.data
    )

    return response.data

  } catch (error) {

    console.error(
      'Backend health check failed:',
      error
    )

    throw error
  }
}


// ============================================================
// FEEDBACK HEALTH
// ============================================================
//
// GET:
// /feedback/health
//
// Your Swagger documentation shows this endpoint.
// ============================================================

export async function checkFeedbackHealth() {

  try {

    const response = await client.get(
      '/feedback/health'
    )

    return response.data

  } catch (error) {

    console.error(
      'Feedback health check failed:',
      error
    )

    throw error
  }
}


// ============================================================
// ERROR HANDLER
// ============================================================

export function getErrorMessage(error) {

  // ----------------------------------------------------------
  // FastAPI HTTPException
  // ----------------------------------------------------------

  if (
    error?.response?.data?.detail
  ) {

    const detail =
      error.response.data.detail

    if (typeof detail === 'string') {
      return detail
    }

    return JSON.stringify(detail)
  }


  // ----------------------------------------------------------
  // Validation Error
  // ----------------------------------------------------------

  if (
    error?.response?.status === 422
  ) {

    return (
      'Invalid request. Please check your submitted data.'
    )
  }


  // ----------------------------------------------------------
  // Not Found
  // ----------------------------------------------------------

  if (
    error?.response?.status === 404
  ) {

    return (
      'API endpoint was not found. ' +
      'Please check the backend URL and endpoint.'
    )
  }


  // ----------------------------------------------------------
  // Unauthorized
  // ----------------------------------------------------------

  if (
    error?.response?.status === 401
  ) {

    return (
      'Authentication failed.'
    )
  }


  // ----------------------------------------------------------
  // Forbidden
  // ----------------------------------------------------------

  if (
    error?.response?.status === 403
  ) {

    return (
      'Request was blocked by the backend.'
    )
  }


  // ----------------------------------------------------------
  // Server Error
  // ----------------------------------------------------------

  if (
    error?.response?.status >= 500
  ) {

    return (
      'The AI backend encountered an error. ' +
      'Please try again.'
    )
  }


  // ----------------------------------------------------------
  // Timeout
  // ----------------------------------------------------------

  if (
    error?.code === 'ECONNABORTED' ||
    error?.code === 'ETIMEDOUT'
  ) {

    return (
      'The request took too long. ' +
      'The AI agents may still be processing. ' +
      'Please try again.'
    )
  }


  // ----------------------------------------------------------
  // Network Error
  // ----------------------------------------------------------

  if (
    error?.message === 'Network Error'
  ) {

    return (
      'Could not connect to the DSA Coach backend. ' +
      'Please check that the backend is running.'
    )
  }


  // ----------------------------------------------------------
  // Generic Error
  // ----------------------------------------------------------

  return (
    error?.message ||
    'Something went wrong. Please try again.'
  )
}


// ============================================================
// GET BACKEND URL
// ============================================================
//
// Useful for debugging.
// ============================================================

export function getBackendUrl() {
  return BASE_URL
}


// ============================================================
// DEFAULT AXIOS CLIENT
// ============================================================

export default client