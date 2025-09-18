import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Video, Image, FileText, Send, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { videoAPI, imageAPI, pdfAPI } from '../services/api';
import { useWebSocket } from '../contexts/WebSocketContext';
import ProgressBar from './ProgressBar';
import ResultSection from './ResultSection';

const GeneratorContainer = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 0.5rem;
  color: #333;
  font-size: 2.5rem;
  font-weight: 700;
`;

const Subtitle = styled.p`
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const ContentTypeSelector = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
`;

const ContentTypeButton = styled.button`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border: 2px solid ${props => props.$active ? '#667eea' : 'rgba(0, 0, 0, 0.1)'};
  border-radius: 12px;
  background: ${props => props.$active ? 'rgba(102, 126, 234, 0.1)' : 'white'};
  color: ${props => props.$active ? '#667eea' : '#666'};
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
  
  &:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }
`;

const PromptInput = styled.textarea`
  width: 100%;
  min-height: 120px;
  padding: 1rem;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
  
  &::placeholder {
    color: #999;
  }
`;

const GenerateButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ContentGenerator = () => {
  const [contentType, setContentType] = useState('video');
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const { taskUpdates, subscribeToTask, unsubscribeFromTask } = useWebSocket();

  const contentTypeOptions = [
    { value: 'video', label: 'Video', icon: Video },
    { value: 'image', label: 'Image', icon: Image },
    { value: 'pdf', label: 'PDF', icon: FileText }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    setCurrentTask(null);

    try {
      let response;
      
      switch (contentType) {
        case 'video':
          response = await videoAPI.generate(prompt);
          break;
        case 'image':
          response = await imageAPI.generate(prompt);
          break;
        case 'pdf':
          response = await pdfAPI.generate(prompt, 'Generated Document');
          break;
        default:
          throw new Error('Invalid content type');
      }

      if (response.success) {
        setCurrentTask(response.taskId);
        subscribeToTask(response.taskId);
        toast.success(`${contentType.charAt(0).toUpperCase() + contentType.slice(1)} generation started!`);
      } else {
        throw new Error(response.error || 'Generation failed');
      }

    } catch (error) {
      console.error('Generation error:', error);
      toast.error(error.message || 'Failed to start generation');
      setIsGenerating(false);
    }
  };

  // Handle task updates
  React.useEffect(() => {
    if (currentTask && taskUpdates[currentTask]) {
      const task = taskUpdates[currentTask];
      
      if (task.status === 'completed') {
        setIsGenerating(false);
        unsubscribeFromTask();
        toast.success(`${contentType.charAt(0).toUpperCase() + contentType.slice(1)} generated successfully!`);
      } else if (task.status === 'failed') {
        setIsGenerating(false);
        unsubscribeFromTask();
        toast.error(task.error || 'Generation failed');
      }
    }
  }, [currentTask, taskUpdates, contentType, unsubscribeFromTask]);

  const currentTaskData = currentTask ? taskUpdates[currentTask] : null;

  return (
    <GeneratorContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Title>Generate AI Content</Title>
      <Subtitle>Create videos, images, and PDFs with the power of AI</Subtitle>

      <Form onSubmit={handleSubmit}>
        <ContentTypeSelector>
          {contentTypeOptions.map((option) => {
            const Icon = option.icon;
            return (
              <ContentTypeButton
                key={option.value}
                type="button"
                $active={contentType === option.value}
                onClick={() => setContentType(option.value)}
                disabled={isGenerating}
              >
                <Icon size={24} />
                {option.label}
              </ContentTypeButton>
            );
          })}
        </ContentTypeSelector>

        <PromptInput
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={`Describe what you want to generate...`}
          disabled={isGenerating}
        />

        <GenerateButton type="submit" disabled={isGenerating || !prompt.trim()}>
          {isGenerating ? (
            <>
              <Loader2 size={20} className="spin" />
              Generating...
            </>
          ) : (
            <>
              <Send size={20} />
              Generate {contentType.charAt(0).toUpperCase() + contentType.slice(1)}
            </>
          )}
        </GenerateButton>
      </Form>

      {currentTaskData && (
        <>
          <ProgressBar 
            progress={currentTaskData.progress} 
            message={currentTaskData.message}
          />
          
          {currentTaskData.status === 'completed' && currentTaskData.data && (
            <ResultSection 
              taskData={currentTaskData}
              contentType={contentType}
            />
          )}
        </>
      )}
    </GeneratorContainer>
  );
};

export default ContentGenerator;
