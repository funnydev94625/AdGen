import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { BarChart3, Clock, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { statusAPI } from '../services/api';
import toast from 'react-hot-toast';

const DashboardContainer = styled.div`
  min-height: 100vh;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const DashboardHeader = styled(motion.div)`
  text-align: center;
  margin-bottom: 3rem;
`;

const DashboardTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const DashboardSubtitle = styled.p`
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
`;

const StatCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`;

const StatIcon = styled.div`
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: white;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.5rem;
`;

const StatLabel = styled.div`
  color: #666;
  font-weight: 500;
`;

const TasksSection = styled(motion.div)`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #5a6fd8;
  }
`;

const TasksList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const TaskItem = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
`;

const TaskInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const TaskType = styled.div`
  padding: 0.25rem 0.75rem;
  background: #667eea;
  color: white;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
`;

const TaskDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const TaskMessage = styled.div`
  color: #333;
  font-weight: 500;
`;

const TaskTime = styled.div`
  color: #666;
  font-size: 0.8rem;
`;

const TaskStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    failed: 0,
    running: 0
  });

  const fetchTasks = async () => {
    try {
      const response = await statusAPI.getAllTasks();
      if (response.success) {
        setTasks(response.tasks);
        calculateStats(response.tasks);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
      toast.error('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (tasksList) => {
    const stats = {
      total: tasksList.length,
      completed: tasksList.filter(task => task.status === 'completed').length,
      failed: tasksList.filter(task => task.status === 'failed').length,
      running: tasksList.filter(task => task.status === 'running').length
    };
    setStats(stats);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={20} color="#22c55e" />;
      case 'failed':
        return <XCircle size={20} color="#ef4444" />;
      case 'running':
        return <Clock size={20} color="#f59e0b" />;
      default:
        return <Clock size={20} color="#6b7280" />;
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <DashboardContainer>
      <DashboardHeader
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <DashboardTitle>Dashboard</DashboardTitle>
        <DashboardSubtitle>Monitor your AI content generation tasks</DashboardSubtitle>
      </DashboardHeader>

      <StatsGrid>
        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <StatIcon>
            <BarChart3 size={24} />
          </StatIcon>
          <StatValue>{stats.total}</StatValue>
          <StatLabel>Total Tasks</StatLabel>
        </StatCard>

        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <StatIcon>
            <CheckCircle size={24} />
          </StatIcon>
          <StatValue>{stats.completed}</StatValue>
          <StatLabel>Completed</StatLabel>
        </StatCard>

        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <StatIcon>
            <Clock size={24} />
          </StatIcon>
          <StatValue>{stats.running}</StatValue>
          <StatLabel>Running</StatLabel>
        </StatCard>

        <StatCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <StatIcon>
            <XCircle size={24} />
          </StatIcon>
          <StatValue>{stats.failed}</StatValue>
          <StatLabel>Failed</StatLabel>
        </StatCard>
      </StatsGrid>

      <TasksSection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <SectionHeader>
          <SectionTitle>Recent Tasks</SectionTitle>
          <RefreshButton onClick={fetchTasks} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'spin' : ''} />
            Refresh
          </RefreshButton>
        </SectionHeader>

        <TasksList>
          {tasks.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
              No tasks found
            </div>
          ) : (
            tasks.slice(0, 10).map((task, index) => (
              <TaskItem
                key={task.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <TaskInfo>
                  <TaskType>{task.type}</TaskType>
                  <TaskDetails>
                    <TaskMessage>{task.message}</TaskMessage>
                    <TaskTime>{formatTime(task.createdAt)}</TaskTime>
                  </TaskDetails>
                </TaskInfo>
                <TaskStatus>
                  {getStatusIcon(task.status)}
                  <span style={{ 
                    color: task.status === 'completed' ? '#22c55e' : 
                           task.status === 'failed' ? '#ef4444' : 
                           task.status === 'running' ? '#f59e0b' : '#6b7280',
                    fontWeight: '500',
                    textTransform: 'capitalize'
                  }}>
                    {task.status}
                  </span>
                </TaskStatus>
              </TaskItem>
            ))
          )}
        </TasksList>
      </TasksSection>
    </DashboardContainer>
  );
};

export default Dashboard;
