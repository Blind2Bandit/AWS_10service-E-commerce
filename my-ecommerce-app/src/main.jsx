import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { Amplify } from 'aws-amplify'

// Configure Amplify v6
Amplify.configure({
  
  // --- CORRECT AUTH v6 CONFIG ---
  Auth: {
    Cognito: {
      region: import.meta.env.VITE_AWS_REGION,
      userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
      userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID
    }
  },
  
  API: {
    REST: {
      ECommerceAPI: {
        endpoint: import.meta.env.VITE_API_GATEWAY_URL,
        region: import.meta.env.VITE_AWS_REGION
      }
    }
  }
});
// -------------------------

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)