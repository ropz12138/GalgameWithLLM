import React, { useState, useEffect, FormEvent } from 'react';
import './App.css'; // We will create this for basic styling
import Login from './components/Login';

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
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const GAME_API_BASE_URL = `${API_BASE_URL}/api`;
const AUTH_API_BASE_URL = API_BASE_URL;

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDialogueModal, setShowDialogueModal] = useState(false);
  const [currentNpcDialogue, setCurrentNpcDialogue] = useState<NPC | null>(null);
  const [npcChatInput, setNpcChatInput] = useState('');
  const [npcDialogueHistory, setNpcDialogueHistory] = useState<DialogueEntry[]>([]);

  // 控制台相关状态
  const [showConsole, setShowConsole] = useState(false);
  const [consoleData, setConsoleData] = useState<any>(null);
  const [consoleLoading, setConsoleLoading] = useState(false);

  // 新增：跟踪五感信息展开状态的状态变量
  const [expandedSensoryItems, setExpandedSensoryItems] = useState<Set<number>>(new Set());

  // 新增：认证状态
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  // 检查本地存储的token
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
    } else {
      setIsLoading(false);
    }
  }, []);

  // 处理登录成功
  const handleLogin = (newToken: string) => {
    setToken(newToken);
    setIsAuthenticated(true);
  };

  // 处理登出
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsAuthenticated(false);
    setGameState(null);
    setError(null);
  };

  // Fetch initial game state - 只在认证后调用
  useEffect(() => {
    if (!isAuthenticated || !token) {
      setIsLoading(false);
      return;
    }

    const fetchGameState = async () => {
      try {
        console.log("🔍 [前端DEBUG] 开始获取游戏状态");
        setIsLoading(true);
        const response = await fetch(`${GAME_API_BASE_URL}/game_state`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        console.log(`🔍 [前端DEBUG] 游戏状态API响应: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
          if (response.status === 401) {
            // Token无效，清除认证状态
            handleLogout();
            return;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("🔍 [前端DEBUG] 接收到的游戏状态数据:", data);
        console.log("🔍 [前端DEBUG] 当前地点的NPC:", data.npcs_at_current_location);
        
        setGameState(data);
        setIsLoading(false);
        console.log("🔍 [前端DEBUG] 游戏状态设置完成");
      } catch (e) {
        console.error("❌ [前端DEBUG] 获取游戏状态失败:", e);
        if (e instanceof Error) {
          setError(`获取游戏状态失败: ${e.message}`);
        }
        setIsLoading(false);
      }
    };
    fetchGameState();
  }, [isAuthenticated, token]);

  // 如果未认证，显示登录页面
  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  const handleUserInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  const handleUserInputSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!userInput.trim() || !gameState || isLoading) return;

    // 保存当前输入，立即清空输入框和设置loading状态
    const currentAction = userInput.trim();
    setUserInput('');
    setIsLoading(true);

    // 添加详细日志
    console.log(`🔍 [前端] 用户输入处理开始:`);
    console.log(`  📝 用户输入: "${currentAction}"`);
    console.log(`  📊 当前游戏状态:`, gameState);
    console.log(`  💬 当前对话历史长度: ${gameState.dialogue_history.length}`);

    try {
      console.log(`🚀 [前端] 发送API请求: ${currentAction}`);
      const response = await fetch(`${GAME_API_BASE_URL}/process_action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ action: currentAction }),
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token无效，清除认证状态
          handleLogout();
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const updatedGameState = await response.json();
      console.log(`✅ [前端] API响应成功:`);
      console.log(`  📊 更新后的游戏状态:`, updatedGameState);
      console.log(`  💬 更新后对话历史长度: ${updatedGameState.dialogue_history.length}`);
      console.log(`  💬 对话历史内容:`, updatedGameState.dialogue_history);
      
      setGameState(updatedGameState);

    } catch (e) {
      console.error(`❌ [前端] 请求失败: ${currentAction}`, e);
      if (e instanceof Error) {
        const errorEntry: DialogueEntry = { speaker: "系统", message: `处理动作时发生错误: ${e.message}` };
        setGameState(prevState => prevState ? { 
          ...prevState, 
          dialogue_history: [...prevState.dialogue_history, errorEntry] 
        } : null);
        setError(`处理动作失败: ${e.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleNpcButtonClick = async (npc: NPC) => {
    setCurrentNpcDialogue(npc);
    setShowDialogueModal(true);
    
    // 从主游戏历史中提取与该NPC的对话记录
    const npcDialogueEntries = gameState?.dialogue_history.filter(entry => 
      entry.speaker === npc.name || 
      (entry.speaker === "玩家" && entry.message.includes(`对${npc.name}说`)) ||
      (entry.speaker === npc.name && entry.message.includes("回复"))
    ) || [];
    
    setNpcDialogueHistory(npcDialogueEntries);
  };

  const handleNpcChatInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNpcChatInput(event.target.value);
  };

  const handleNpcChatSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!npcChatInput.trim() || !currentNpcDialogue) return;

    const currentInput = npcChatInput.trim();
    const dialogueMessage = `和${currentNpcDialogue.name}说话：${currentInput}`;
    setNpcChatInput('');

    // 添加详细日志
    console.log(`🔍 [前端] NPC对话处理开始:`);
    console.log(`  📝 NPC输入: "${currentInput}"`);
    console.log(`  🗣️ 构造的对话消息: "${dialogueMessage}"`);
    console.log(`  👤 目标NPC: ${currentNpcDialogue.name}`);
    console.log(`  📊 当前游戏状态:`, gameState);
    console.log(`  💬 当前对话历史长度: ${gameState?.dialogue_history.length || 0}`);

    try {
      console.log(`🗣️ [前端] 发送NPC对话请求: ${dialogueMessage}`);
      // 使用统一的process_action API
      const response = await fetch(`${GAME_API_BASE_URL}/process_action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ action: dialogueMessage }),
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token无效，清除认证状态
          handleLogout();
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const updatedGameState = await response.json();
      console.log(`✅ [前端] NPC对话请求成功:`);
      console.log(`  📊 更新后的游戏状态:`, updatedGameState);
      console.log(`  💬 更新后对话历史长度: ${updatedGameState.dialogue_history.length}`);
      console.log(`  💬 对话历史内容:`, updatedGameState.dialogue_history);
      
      setGameState(updatedGameState);
      
      // 更新模态窗口中的对话历史
      const npcDialogueEntries = updatedGameState.dialogue_history.filter((entry: DialogueEntry) => 
        entry.speaker === currentNpcDialogue.name || 
        (entry.speaker === "玩家" && entry.message.includes(`对${currentNpcDialogue.name}说`)) ||
        (entry.speaker === currentNpcDialogue.name && entry.message.includes("回复"))
      ) || [];
      
      console.log(`  💬 NPC专用对话历史:`, npcDialogueEntries);
      setNpcDialogueHistory(npcDialogueEntries);
      
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : String(e);
      console.error(`❌ [前端] NPC对话请求失败: ${dialogueMessage}`, errorMsg);
      // 显示错误消息
      const errorEntry: DialogueEntry = { speaker: "系统", message: `与NPC对话出错: ${errorMsg}` };
      setNpcDialogueHistory(prev => [...prev, errorEntry]);
    }
  };

  // 解析系统消息中的感官描述
  const parseSensoryMessage = (message: string) => {
    try {
      // 尝试解析JSON格式的感官描述
      const jsonMatch = message.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const jsonData = JSON.parse(jsonMatch[0]);
        if (jsonData.vision || jsonData.hearing || jsonData.smell || jsonData.touch) {
          return {
            vision: jsonData.vision || '',
            hearing: jsonData.hearing || '',
            smell: jsonData.smell || '',
            touch: jsonData.touch || ''
          };
        }
      }
    } catch (e) {
      // 如果解析失败，返回null表示这不是感官描述消息
    }
    return null;
  };

  // 切换五感信息展开状态的函数
  const toggleSensoryExpansion = (index: number) => {
    const newExpandedItems = new Set(expandedSensoryItems);
    if (newExpandedItems.has(index)) {
      newExpandedItems.delete(index);
    } else {
      newExpandedItems.add(index);
    }
    setExpandedSensoryItems(newExpandedItems);
  };

  // 渲染对话条目
  const renderDialogueEntry = (entry: DialogueEntry, index: number) => {
    const speakerClass = `dialogue-entry speaker-${entry.speaker.toLowerCase().replace(' ', '-')}`;
    
    // 检查是否是系统的感官描述消息
    if (entry.speaker === "系统") {
      const sensoryData = parseSensoryMessage(entry.message);
      if (sensoryData) {
        const isExpanded = expandedSensoryItems.has(index);
        
        // 获取第一行文本（从第一个感官信息中提取）
        const firstSensoryItem = sensoryData.vision || sensoryData.hearing || sensoryData.smell || sensoryData.touch || '';
        const firstLine = firstSensoryItem.length > 50 ? firstSensoryItem.substring(0, 50) + '...' : firstSensoryItem;
        
        return (
          <div key={index} className={`${speakerClass} sensory-description`}>
            <div 
              className="sensory-header"
              onClick={() => toggleSensoryExpansion(index)}
              style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', marginBottom: '5px' }}
            >
              <span style={{ marginRight: '8px' }}>
                {isExpanded ? '🔽' : '▶️'}
              </span>
              <strong>感官体验：</strong>
              {!isExpanded && <span style={{ marginLeft: '8px', color: '#666' }}>{firstLine}</span>}
            </div>
            
            {isExpanded && (
              <div className="sensory-content">
            {sensoryData.vision && (
              <div className="sensory-item">
                <strong>视觉：</strong>{sensoryData.vision}
              </div>
            )}
            {sensoryData.hearing && (
              <div className="sensory-item">
                <strong>听觉：</strong>{sensoryData.hearing}
              </div>
            )}
            {sensoryData.smell && (
              <div className="sensory-item">
                <strong>嗅觉：</strong>{sensoryData.smell}
              </div>
            )}
            {sensoryData.touch && (
              <div className="sensory-item">
                <strong>触觉：</strong>{sensoryData.touch}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      }
    }
    
    // 普通消息的渲染
    return (
      <p key={index} className={speakerClass}>
        <strong>{entry.speaker}:</strong> {entry.message}
      </p>
    );
  };

  // 获取控制台数据的函数
  const fetchConsoleData = async () => {
    console.log("🔍 [前端DEBUG] 开始获取控制台数据");
    setConsoleLoading(true);
    try {
      console.log("🔍 [前端DEBUG] 发送API请求...");
      const [locationsResponse, npcStatusResponse] = await Promise.all([
        fetch(`${GAME_API_BASE_URL}/debug/locations`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch(`${GAME_API_BASE_URL}/debug/npc_status`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      ]);

      console.log("🔍 [前端DEBUG] API响应状态:");
      console.log(`  - locationsResponse: ${locationsResponse.status} ${locationsResponse.statusText}`);
      console.log(`  - npcStatusResponse: ${npcStatusResponse.status} ${npcStatusResponse.statusText}`);

      if (!locationsResponse.ok || !npcStatusResponse.ok) {
        if (locationsResponse.status === 401 || npcStatusResponse.status === 401) {
          // Token无效，清除认证状态
          handleLogout();
          return;
        }
        throw new Error('获取控制台数据失败');
      }

      const locationsData = await locationsResponse.json();
      const npcStatusData = await npcStatusResponse.json();

      console.log("🔍 [前端DEBUG] 接收到的数据:");
      console.log("  - locationsData:", locationsData);
      console.log("  - npcStatusData:", npcStatusData);

      setConsoleData({
        locations: locationsData,
        npcs: npcStatusData
      });

      console.log("🔍 [前端DEBUG] 控制台数据设置完成");
    } catch (error) {
      console.error('❌ [前端DEBUG] 获取控制台数据失败:', error);
      alert('获取控制台数据时出错');
    } finally {
      setConsoleLoading(false);
    }
  };

  // 打开控制台时自动获取数据
  const openConsole = () => {
    setShowConsole(true);
    fetchConsoleData();
  };

  if (error) {
    return <div className="error">错误: {error}</div>;
  }

  if (isLoading && !gameState) {
    return <div className="loading">游戏加载中...</div>;
  }

  if (!gameState) {
    return <div className="loading">正在连接游戏服务器...</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>影视片场文字冒险游戏</h1>
        <div className="header-controls">
          <button 
            className="console-button"
            onClick={openConsole}
            disabled={consoleLoading}
          >
            {consoleLoading ? '加载中...' : '控制台'}
          </button>
          <button 
            className="logout-button"
            onClick={handleLogout}
          >
            登出
          </button>
        </div>
      </header>

      <div className="App">
        <div className="game-container">
          <header className="App-header">
            <div className="location-info">
              <h2>当前地点: {locationKeyToName[gameState.player_location] || gameState.player_location} ({gameState.current_time})</h2>
              <p>{gameState.location_description}</p>
              <p>可前往: {gameState.connected_locations.map(location => locationKeyToName[location] || location).join(', ')}</p>
            </div>
            
            {gameState.npcs_at_current_location.length > 0 && (
              <div className="npcs-section">
                <h3>当前地点的NPC：</h3>
                {(() => {
                  console.log("🔍 [前端DEBUG] 渲染页面NPC列表:");
                  console.log("  - gameState.npcs_at_current_location:", gameState.npcs_at_current_location);
                  return null;
                })()}
                <div className="npc-list">
                  {gameState.npcs_at_current_location.map((npc) => {
                    console.log(`🔍 [前端DEBUG] 渲染页面NPC卡片: ${npc.name}`, npc);
                    return (
                      <div key={npc.name} className="npc-card">
                        <h4>{npc.name}</h4>
                        <p>正在进行：{npc.event}</p>
                        <p>性格：{npc.personality}</p>
                        <div className="npc-actions">
                          <button onClick={() => handleNpcButtonClick(npc)} className="detailed-talk-btn">
                            与{npc.name}对话
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </header>

          <main className="dialogue-section">
            <h3>游戏记录：</h3>
            <div className="dialogue-history">
              {gameState.dialogue_history.map((entry, index) => (
                renderDialogueEntry(entry, index))
              )}
            </div>
          </main>

          <footer className="App-footer">
            <div className="input-hints">
              <p>💡 提示：你可以输入类似"前往 主摄影棚"、"和林若曦说话：你好"、"查看周围"等指令</p>
            </div>
            <form onSubmit={handleUserInputSubmit} className="input-form">
              <input
                type="text"
                value={userInput}
                onChange={handleUserInputChange}
                placeholder="请输入你的行动... (例如：前往 主摄影棚 或 和林若曦说话：你好)"
                className="user-input"
                disabled={isLoading}
              />
              <button type="submit" className="submit-button" disabled={isLoading}>
                {isLoading ? '处理中...' : '执行'}
              </button>
            </form>
          </footer>

          {/* NPC对话模态窗口 */}
          {showDialogueModal && currentNpcDialogue && (
            <div className="modal-overlay" onClick={() => setShowDialogueModal(false)}>
              <div className="dialogue-modal" onClick={(e) => e.stopPropagation()}>
                <h3>与{currentNpcDialogue.name}对话</h3>
                <div className="npc-dialogue-history">
                  {npcDialogueHistory.map((entry, index) => renderDialogueEntry(entry, index))}
                </div>
                <form onSubmit={handleNpcChatSubmit}>
                  <input
                    type="text"
                    value={npcChatInput}
                    onChange={handleNpcChatInputChange}
                    placeholder={`对${currentNpcDialogue.name}说些什么...`}
                    className="npc-chat-input"
                  />
                  <button type="submit" disabled={!npcChatInput.trim()}>发送</button>
                </form>
                <button onClick={() => setShowDialogueModal(false)} className="close-modal-button">关闭</button>
              </div>
            </div>
          )}

          {/* 控制台模态窗口 */}
          {showConsole && (
            <div className="modal-overlay" onClick={() => setShowConsole(false)}>
              <div className="console-modal" onClick={(e) => e.stopPropagation()}>
                <div className="console-header">
                  <h3>开发者控制台</h3>
                  <div className="console-controls">
                    <button onClick={fetchConsoleData} disabled={consoleLoading}>
                      {consoleLoading ? '刷新中...' : '刷新数据'}
                    </button>
                    <button onClick={() => setShowConsole(false)} className="close-button">关闭</button>
                  </div>
                </div>
                
                {consoleLoading && <div className="loading">加载控制台数据中...</div>}
                
                {consoleData && (
                  <div className="console-content">
                    {/* 地点信息面板 */}
                    <div className="console-panel">
                      <h4>地点信息 ({consoleData.locations?.total_count || 0}个地点)</h4>
                      <div className="locations-grid">
                        {consoleData.locations?.locations && Object.entries(consoleData.locations.locations).map(([key, location]: [string, any]) => (
                          <div key={key} className={`location-card ${location.is_dynamic ? 'dynamic-location' : 'static-location'}`}>
                            <div className="location-header">
                              <strong>{location.name}</strong>
                              <span className="location-key">({key})</span>
                              {location.is_dynamic && <span className="dynamic-badge">动态</span>}
                            </div>
                            <p className="location-description">{location.description}</p>
                            {location.connections && location.connections.length > 0 && (
                              <div className="location-connections">
                                <strong>连接：</strong>{location.connections.join(', ')}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* NPC信息面板 */}
                    <div className="console-panel">
                      <h4>NPC状态信息</h4>
                      {(() => {
                        console.log("🔍 [前端DEBUG] 渲染控制台NPC状态信息:");
                        console.log("  - consoleData.npcs:", consoleData.npcs);
                        console.log("  - npcs_at_player_location:", consoleData.npcs?.npcs_at_player_location);
                        console.log("  - npc_locations:", consoleData.npcs?.npc_locations);
                        return null;
                      })()}
                      <div className="npc-status-info">
                        <p><strong>当前时间：</strong>{consoleData.npcs?.current_time}</p>
                        <p><strong>玩家位置：</strong>{consoleData.npcs?.player_location}</p>
                        <p><strong>玩家当前位置的NPC：</strong>
                          {consoleData.npcs?.npcs_at_player_location?.length > 0 
                            ? consoleData.npcs.npcs_at_player_location.map((npc: any) => npc.name).join(', ')
                            : '无'
                          }
                        </p>
                      </div>
                      <div className="npcs-grid">
                        {consoleData.npcs?.npc_locations && Object.entries(consoleData.npcs.npc_locations).map(([name, npcInfo]: [string, any]) => {
                          console.log(`🔍 [前端DEBUG] 渲染NPC卡片: ${name}`, npcInfo);
                          return (
                            <div key={name} className="npc-status-card">
                              <h5>{name}</h5>
                              <p><strong>当前位置：</strong>{npcInfo.current_location}</p>
                              <p><strong>当前活动：</strong>{npcInfo.current_event}</p>
                              <p><strong>性格：</strong>{npcInfo.personality}</p>
                              <div className="npc-schedule">
                                <strong>计划表：</strong>
                                <ul>
                                  {npcInfo.schedule && npcInfo.schedule.length > 0 ? (
                                    npcInfo.schedule.map((item: any, index: number) => (
                                      <li key={index}>
                                        {item.start_time}-{item.end_time} 在{item.location}：{item.event}
                                      </li>
                                    ))
                                  ) : (
                                    <li>无计划</li>
                                  )}
                                </ul>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

