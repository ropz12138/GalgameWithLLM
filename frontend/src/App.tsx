import React, { useState, useEffect, FormEvent } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoginPage } from './components/LoginPage';
import { RegisterPage } from './components/RegisterPage';
import { GamePage } from './components/GamePage';
import './App.css'; // We will create this for basic styling

interface NPC {
  name: string;
  event: string;
  personality: string;
}

interface DialogueEntry {
  speaker: string;
  message: string;
}

interface GameState {
  player_location: string;
  current_time: string;
  location_description: string;
  connected_locations: string[];
  npcs_at_current_location: NPC[];
  dialogue_history: DialogueEntry[];
}

const locationKeyToName: Record<string, string> = {
  "linkai_room": "林凯房间",
  "linruoxi_room": "林若曦房间",
  "zhangyuqing_room": "张雨晴房间",
  "livingroom": "客厅",
  "kitchen": "厨房",
  "bathroom": "卫生间"
};

// API基础URL - 从环境变量读取，默认为8001端口
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

// 受保护的路由组件
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
        return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">正在验证身份...</p>
              </div>
          </div>
        );
      }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// 公开路由组件（已登录用户重定向到游戏页面）
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">正在验证身份...</p>
        </div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/galgame" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* 默认路由重定向到登录页 */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* 公开路由 */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            } 
          />
          
          {/* 受保护的路由 */}
          <Route 
            path="/galgame" 
            element={
              <ProtectedRoute>
                <GamePage />
              </ProtectedRoute>
            } 
          />
          
          {/* 404页面 */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

