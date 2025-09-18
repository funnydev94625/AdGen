import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import ContentGenerator from '../components/ContentGenerator';
import FeaturesSection from '../components/FeaturesSection';

const HomeContainer = styled.div`
  min-height: 100vh;
  padding: 2rem;
`;

const HeroSection = styled(motion.div)`
  text-align: center;
  margin-bottom: 4rem;
`;

const HeroTitle = styled.h1`
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const HeroSubtitle = styled.p`
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
`;

const Home = () => {
  return (
    <HomeContainer>
      <HeroSection
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <HeroTitle>AI Content Generator</HeroTitle>
        <HeroSubtitle>
          Create stunning videos, images, and PDFs with the power of artificial intelligence. 
          Just describe what you want, and we'll bring it to life.
        </HeroSubtitle>
      </HeroSection>

      <ContentGenerator />

      <FeaturesSection />
    </HomeContainer>
  );
};

export default Home;
