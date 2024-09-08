import logo from './logo.svg';
import './App.css';
import React from 'react';
import { useEffect } from 'react';
import { Amplify } from 'aws-amplify';
import { Loader, ThemeProvider } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import { FaceLivenessDetector } from '@aws-amplify/ui-react-liveness';
import {
  View,
  Flex,
  Alert,
  Image
} from '@aws-amplify/ui-react';
import awsExports from "./aws-exports";
Amplify.configure(awsExports);

function App() {

  const [faceLivenessAnalysis, setFaceLivenessAnalysis] = React.useState(null)

  const getfaceLivenessAnalysis = (faceLivenessAnalysis) => {
    if (faceLivenessAnalysis !== null) {
      setFaceLivenessAnalysis(faceLivenessAnalysis)
    }
  }

  const tryagain = () =>{
    setFaceLivenessAnalysis(null)
  }


  return (
    <ThemeProvider>
      <Flex
        direction="row"
        justifyContent="center"
        alignItems="center"
        alignContent="flex-start"
        wrap="nowrap"
        gap="1rem"
      >
        <View
          as="div"
          maxHeight="600px"
          height="600px"
          width="740px"
          maxWidth="740px"
        >
          {faceLivenessAnalysis && faceLivenessAnalysis.Confidence ? (
            <ReferenceImage faceLivenessAnalysis={faceLivenessAnalysis} tryagain={tryagain}></ReferenceImage>
          ) :
            (<FaceLiveness faceLivenessAnalysis={getfaceLivenessAnalysis} />)}

        </View>
      </Flex>
    </ThemeProvider>


  );
}

export default App;