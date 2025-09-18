import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Download, CheckCircle, Eye } from 'lucide-react';
import { downloadAPI } from '../services/api';

const ResultContainer = styled(motion.div)`
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(34, 197, 94, 0.2);
`;

const ResultHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const ResultTitle = styled.h3`
  color: #22c55e;
  font-size: 1.1rem;
  font-weight: 600;
`;

const ResultMessage = styled.p`
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid ${props => props.$primary ? '#22c55e' : 'rgba(0, 0, 0, 0.1)'};
  border-radius: 8px;
  background: ${props => props.$primary ? '#22c55e' : 'white'};
  color: ${props => props.$primary ? 'white' : '#666'};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
`;

const PreviewContainer = styled.div`
  margin-top: 1rem;
  text-align: center;
`;

const PreviewImage = styled.img`
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
`;

const ResultSection = ({ taskData, contentType }) => {
  console.log(taskData);
  const getFilename = () => {
    if (taskData.data?.videoPath && typeof taskData.data.videoPath === 'string') {
      return taskData.data.videoPath.split(/[\\/]/).pop();
    } else if (taskData.data?.imagePath && typeof taskData.data.imagePath === 'string') {
      return taskData.data.imagePath.split(/[\\/]/).pop();
    } else if (taskData.data?.pdfPath && typeof taskData.data.pdfPath === 'string') {
      return taskData.data.pdfPath.split(/[\\/]/).pop();
    }
    return null;
  };

  const getDownloadUrl = () => {
    const filename = getFilename();
    return filename ? downloadAPI.getDownloadUrl(filename) : null;
  };

  const handleDownload = () => {
    const filename = getFilename();
    if (filename) {
      downloadAPI.downloadFile(filename);
    }
  };

  const handlePreview = () => {
    const url = getDownloadUrl();
    if (url) {
      window.open(url, '_blank');
    }
  };

  const filename = getFilename();
  const downloadUrl = getDownloadUrl();

  return (
    <ResultContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <ResultHeader>
        <CheckCircle size={20} />
        <ResultTitle>
          {contentType.charAt(0).toUpperCase() + contentType.slice(1)} Generated Successfully!
        </ResultTitle>
      </ResultHeader>
      
      <ResultMessage>
        Your {contentType} has been created and is ready for download.
      </ResultMessage>

      {contentType === 'image' && downloadUrl && (
        <PreviewContainer>
          <PreviewImage src={downloadUrl} alt="Generated content" />
        </PreviewContainer>
      )}

      <ActionButtons>
        <ActionButton onClick={handlePreview}>
          <Eye size={18} />
          Preview
        </ActionButton>
        <ActionButton $primary onClick={handleDownload}>
          <Download size={18} />
          Download
        </ActionButton>
      </ActionButtons>
    </ResultContainer>
  );
};

export default ResultSection;
