import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Video, Image, FileText, Zap, Shield, Globe } from 'lucide-react';

const FeaturesContainer = styled(motion.div)`
  margin-top: 4rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
`;

const FeaturesTitle = styled.h2`
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 3rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
`;

const FeatureCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`;

const FeatureIcon = styled.div`
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  color: white;
`;

const FeatureTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
`;

const FeatureDescription = styled.p`
  color: #666;
  line-height: 1.6;
`;

const features = [
  {
    icon: Video,
    title: 'AI Video Generation',
    description: 'Create engaging videos using RunwayML\'s advanced AI technology. Generate professional content from simple text prompts.'
  },
  {
    icon: Image,
    title: 'AI Image Generation',
    description: 'Generate stunning images with DALL-E 3. Create artwork, photos, and graphics that match your vision perfectly.'
  },
  {
    icon: FileText,
    title: 'AI PDF Generation',
    description: 'Create professional PDF documents with structured layouts. Perfect for menus, brochures, and business documents.'
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Our optimized AI models deliver results in seconds, not minutes. Get your content when you need it.'
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'Your data is protected with enterprise-grade security. We never store or share your personal information.'
  },
  {
    icon: Globe,
    title: 'Real-time Updates',
    description: 'Track your generation progress with live updates. Know exactly when your content is ready.'
  }
];

const FeaturesSection = () => {
  return (
    <FeaturesContainer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.3 }}
    >
      <FeaturesTitle>Why Choose AdGen?</FeaturesTitle>
      
      <FeaturesGrid>
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <FeatureCard
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
            >
              <FeatureIcon>
                <Icon size={32} />
              </FeatureIcon>
              <FeatureTitle>{feature.title}</FeatureTitle>
              <FeatureDescription>{feature.description}</FeatureDescription>
            </FeatureCard>
          );
        })}
      </FeaturesGrid>
    </FeaturesContainer>
  );
};

export default FeaturesSection;
