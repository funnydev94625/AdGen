import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

const ProgressContainer = styled(motion.div)`
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
`;

const ProgressHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const ProgressTitle = styled.h3`
  color: #667eea;
  font-size: 1.1rem;
  font-weight: 600;
`;

const ProgressMessage = styled.p`
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
`;

const ProgressBarWrapper = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  overflow: hidden;
`;

const ProgressBarFill = styled(motion.div)`
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
`;

const ProgressPercentage = styled.div`
  text-align: center;
  margin-top: 0.5rem;
  color: #667eea;
  font-weight: 600;
  font-size: 0.9rem;
`;

const ProgressBar = ({ progress, message }) => {
  return (
    <ProgressContainer
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <ProgressHeader>
        <Loader2 size={20} className="spin" />
        <ProgressTitle>Generating Content</ProgressTitle>
      </ProgressHeader>
      
      <ProgressMessage>{message}</ProgressMessage>
      
      <ProgressBarWrapper>
        <ProgressBarFill
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </ProgressBarWrapper>
      
      <ProgressPercentage>{progress}%</ProgressPercentage>
    </ProgressContainer>
  );
};

export default ProgressBar;
