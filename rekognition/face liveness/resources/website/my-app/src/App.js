import React, { useState, useEffect, useCallback } from 'react';
import { Amplify } from 'aws-amplify';
import { FaceLivenessDetector } from '@aws-amplify/ui-react-liveness';
import '@aws-amplify/ui-react/styles.css';
import './App.css';
import { Loader } from '@aws-amplify/ui-react';
import { ThemeProvider } from '@aws-amplify/ui-react';
import {
  View,
  Flex,
} from '@aws-amplify/ui-react';

import awsexports from './aws-exports';

Amplify.configure(awsexports);

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = React.useState(true);
  const [livenessResult, setLivenessResult] = useState(null);
  const [error, setError] = useState(null);
  const [isSessionStarted, setIsSessionStarted] = useState(false);

  const apiGatewayUrl = "https://l5uqb1xmfk.execute-api.us-east-1.amazonaws.com/prod";


  const handleFetchError = async (error, response, method) => {
    let errorMessage = `Error in ${method}: ${error.message}\n`;
    if (response) {
      errorMessage += `Status: ${response.status} ${response.statusText}\n`;
      try {
        const errorBody = await response.text();
        errorMessage += `Response body: ${errorBody}\n`;
      } catch (e) {
        errorMessage += `Couldn't read response body: ${e.message}\n`;
      }
    } else {
      // If there's no response, it's likely a network error
      errorMessage += `Network error: ${error.name}\n`;
      if (error.cause) {
        errorMessage += `Cause: ${error.cause.message}\n`;
      }
    }
    console.error(errorMessage);
    setError(errorMessage);
  };

  useEffect(() => {
    const startLivenessSession = async () => {
      if (!isSessionStarted) return;

      try {
        setError(null);
        const response = await fetch(`${apiGatewayUrl}/start-liveness-session`, {
          method: 'GET',
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSessionId(data.sessionId);
        setLoading(false);
      } catch (error) {
        await handleFetchError(error, error.response, 'startLivenessSession');
      }
    };

    startLivenessSession();
  }, [isSessionStarted, apiGatewayUrl]);

  const getLivenessResult = useCallback(async () => {
    if (!sessionId) {
      await handleFetchError('Session error!', `No session id: ${sessionId}`, 'getLivenessResult');
      return;
    }

    try {
      setError(null);
      const response = await fetch(`${apiGatewayUrl}/liveness-session-result`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ SessionId: sessionId }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setLivenessResult(data);
    } catch (error) {
      await handleFetchError(error, error.response, 'getLivenessResult');
    }
  }, [sessionId, apiGatewayUrl]);

  useEffect(() => {
    if (sessionId) {
      getLivenessResult();
    }
  }, [sessionId, getLivenessResult]);

  const handleAnalysisComplete = useCallback((event) => {
    console.log('Liveness detection completed:', event);
    getLivenessResult();
  }, [getLivenessResult]);

  return (
    <div className="App">
      <h1>Face Liveness Detection</h1>
      <button onClick={() => setIsSessionStarted(true)}>Start Liveness Session</button>
      
      {error && (
        <p style={{ color: 'red', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {error}
        </p>
      )}
      
      {sessionId && (
        <FaceLivenessDetector
          sessionId={sessionId}
          region="us-east-1"
          onAnalysisComplete={handleAnalysisComplete}
        />
      )}
      
      {livenessResult && (
        <div>
          <h2>Liveness Result</h2>
          <p>Confidence: {livenessResult.Confidence}</p>
          <p>Status: {livenessResult.Status}</p>
        </div>
      )}
    </div>
  );
}

export default App;
