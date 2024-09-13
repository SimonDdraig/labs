import React, { useState, useEffect, useCallback } from 'react';
import { Amplify } from 'aws-amplify';
import { FaceLivenessDetector } from '@aws-amplify/ui-react-liveness';
import '@aws-amplify/ui-react/styles.css';
import './App.css';

import awsexports from './aws-exports';

Amplify.configure(awsexports);

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [livenessResult, setLivenessResult] = useState(null);
  const [someInfo, setInfo] = useState(null);
  const [error, setError] = useState(null);
  const [isSessionStarted, setIsSessionStarted] = useState(false);
  const [gettingSession, setGettingSession] = useState(false);

  const apiGatewayUrl = "https://XXXXXXXXX.execute-api.us-east-1.amazonaws.com/poc";


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

      setError(null);
      setGettingSession(true);
      try {
        const response = await fetch(`${apiGatewayUrl}/start-liveness-session`, {
          method: 'GET',
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSessionId(data.sessionId);
      } catch (error) {
        await handleFetchError(error, error.response, 'startLivenessSession');
      }
      setGettingSession(false);
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
      setInfo(`Getting results with: ${apiGatewayUrl}/liveness-session-result?SessionId=${sessionId}`)

      const response = await fetch(`${apiGatewayUrl}/liveness-session-result?SessionId=${sessionId}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setLivenessResult(data);
      setSessionId(null);
    } catch (error) {
      await handleFetchError(error, error.response, 'getLivenessResult');
    }
  }, [sessionId, apiGatewayUrl]);

  const handleAnalysisComplete = useCallback((event) => {
    console.log('Liveness detection completed:', event);
    getLivenessResult();
  }, [getLivenessResult]);

  return (
    <div className="App">
      <h1>Face Liveness Detection</h1>
      <button onClick={() => setIsSessionStarted(true)}>
        Start Liveness Session
      </button>

      {error && (
        <p
          style={{
            color: "red",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {error}
        </p>
      )}

      {gettingSession && (
        <p
          style={{
            color: "green",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          Getting a session id...
        </p>
      )}

      {sessionId && (
        <p
          style={{
            color: "green",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          Got a session id {sessionId}
        </p>
      )}

      {someInfo && (
        <p
          style={{
            color: "green",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {someInfo}
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
