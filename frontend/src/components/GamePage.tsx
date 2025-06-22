import React, { useState, useEffect, FormEvent } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { NewStoryModal } from './NewStoryModal';

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

export function GamePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
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

  // 新建故事弹窗状态
  const [showNewStoryModal, setShowNewStoryModal] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Fetch initial game state
  useEffect(() => {
    const fetchGameState = async () => {
      try {
        console.log("🔍 [前端DEBUG] 开始获取游戏状态");
        setIsLoading(true);
        const response = await fetch(`${API_BASE_URL}/game_state`);
        console.log(`🔍 [前端DEBUG] 游戏状态API响应: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
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
  }, []);

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
      const response = await fetch(`${API_BASE_URL}/process_action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: currentAction }),
      });
      
      if (!response.ok) {
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
      const response = await fetch(`${API_BASE_URL}/process_action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: dialogueMessage }),
      });
      
      if (!response.ok) {
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
      );
      setNpcDialogueHistory(npcDialogueEntries);

    } catch (e) {
      console.error(`❌ [前端] NPC对话请求失败: ${dialogueMessage}`, e);
      if (e instanceof Error) {
        alert(`NPC对话失败: ${e.message}`);
      }
    }
  };

  // 解析五感信息的函数
  const parseSensoryMessage = (message: string) => {
    try {
      const parsed = JSON.parse(message);
      if (typeof parsed === 'object' && parsed !== null) {
        return parsed;
      }
    } catch (e) {
      // 如果解析失败，返回原始消息
    }
    return null;
  };

  // 切换五感信息展开状态
  const toggleSensoryExpansion = (index: number) => {
    const newExpanded = new Set(expandedSensoryItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSensoryItems(newExpanded);
  };

  const renderDialogueEntry = (entry: DialogueEntry, index: number) => {
    const isPlayer = entry.speaker === "玩家";
    const isSystem = entry.speaker === "系统";
    
    // 检查是否是五感反馈消息
    const sensoryData = parseSensoryMessage(entry.message);
    const isExpanded = expandedSensoryItems.has(index);
    
    if (sensoryData) {
      // 渲染五感反馈
      return (
        <div key={index} className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-green-700 font-medium">🌟 五感反馈</span>
            <button
              onClick={() => toggleSensoryExpansion(index)}
              className="text-green-600 hover:text-green-800 text-sm"
            >
              {isExpanded ? '收起' : '展开'}
            </button>
          </div>
          
          {isExpanded ? (
            <div className="space-y-2 text-sm">
              {sensoryData.vision && (
                <div><strong>👁️ 视觉:</strong> {sensoryData.vision}</div>
              )}
              {sensoryData.hearing && (
                <div><strong>👂 听觉:</strong> {sensoryData.hearing}</div>
              )}
              {sensoryData.smell && (
                <div><strong>👃 嗅觉:</strong> {sensoryData.smell}</div>
              )}
              {sensoryData.touch && (
                <div><strong>✋ 触觉:</strong> {sensoryData.touch}</div>
              )}
            </div>
          ) : (
            <div className="text-sm text-green-600">
              点击展开查看详细的五感反馈信息...
            </div>
          )}
        </div>
      );
    }
    
    // 渲染普通对话
    return (
      <div key={index} className={`mb-3 ${isPlayer ? 'text-right' : 'text-left'}`}>
        <div className={`inline-block max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isPlayer 
            ? 'bg-blue-500 text-white' 
            : isSystem 
              ? 'bg-gray-200 text-gray-800' 
              : 'bg-gray-100 text-gray-800'
        }`}>
          <div className="font-semibold text-sm">
            {isPlayer ? '你' : entry.speaker}
          </div>
          <div className="mt-1 text-sm">{entry.message}</div>
        </div>
      </div>
    );
  };

  // 获取控制台数据的函数
  const fetchConsoleData = async () => {
    setConsoleLoading(true);
    try {
      // 并行获取多个调试信息
      const [gameStateRes, npcStatusRes, locationStatusRes] = await Promise.all([
        fetch(`${API_BASE_URL}/debug/game_state`),
        fetch(`${API_BASE_URL}/debug/npc_status`),
        fetch(`${API_BASE_URL}/debug/location_status`)
      ]);

      const [gameStateData, npcStatusData, locationStatusData] = await Promise.all([
        gameStateRes.json(),
        npcStatusRes.json(),
        locationStatusRes.json()
      ]);

      setConsoleData({
        gameState: gameStateData,
        npcStatus: npcStatusData,
        locationStatus: locationStatusData,
        timestamp: new Date().toLocaleString()
      });
    } catch (e) {
      console.error("获取控制台数据失败:", e);
      setConsoleData({
        error: `获取数据失败: ${e instanceof Error ? e.message : '未知错误'}`,
        timestamp: new Date().toLocaleString()
      });
    } finally {
      setConsoleLoading(false);
    }
  };

  // 打开控制台
  const openConsole = () => {
    setShowConsole(true);
    fetchConsoleData();
  };

  if (isLoading && !gameState) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">正在加载游戏状态...</p>
        </div>
      </div>
    );
  }

  if (error && !gameState) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">❌ 加载失败</div>
          <p className="text-gray-600">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">🎮 LLM文字游戏</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">欢迎，{user?.username}</span>
            <button
              onClick={() => setShowNewStoryModal(true)}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              新建故事
            </button>
            <button
              onClick={openConsole}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              调试控制台
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              登出
            </button>
          </div>
        </div>
      </nav>

      {/* 游戏主体内容 */}
      <div className="flex-1 flex">
        {/* 左侧游戏状态面板 */}
        <div className="w-1/3 bg-white border-r p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">游戏状态</h2>
          
          {gameState && (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700">当前位置</h3>
                <p className="text-gray-600">{locationKeyToName[gameState.player_location] || gameState.player_location}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700">当前时间</h3>
                <p className="text-gray-600">{gameState.current_time}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700">位置描述</h3>
                <p className="text-gray-600 text-sm">{gameState.location_description}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700">可前往的位置</h3>
                <div className="flex flex-wrap gap-2 mt-2">
                  {gameState.connected_locations.map((location, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                      {locationKeyToName[location] || location}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-700">当前位置的角色</h3>
                <div className="space-y-2 mt-2">
                  {gameState.npcs_at_current_location.length > 0 ? (
                    gameState.npcs_at_current_location.map((npc, index) => (
                      <div key={index} className="border rounded p-3 bg-gray-50">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-medium">{npc.name}</h4>
                            <p className="text-sm text-gray-600 mt-1">{npc.event}</p>
                            <p className="text-xs text-gray-500 mt-1">{npc.personality}</p>
                          </div>
                          <button
                            onClick={() => handleNpcButtonClick(npc)}
                            className="ml-2 px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
                          >
                            对话
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">当前位置没有其他角色</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 右侧对话和输入区域 */}
        <div className="flex-1 flex flex-col bg-white">
          {/* 对话历史区域 */}
          <div className="flex-1 overflow-y-auto p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">游戏记录</h2>
            <div className="space-y-3">
              {gameState && gameState.dialogue_history.length > 0 ? (
                gameState.dialogue_history.map((entry, index) => renderDialogueEntry(entry, index))
              ) : (
                <p className="text-gray-500">开始你的冒险吧...</p>
              )}
            </div>
          </div>

          {/* 输入区域 */}
          <div className="border-t p-6">
            <form onSubmit={handleUserInputSubmit} className="flex space-x-2">
              <input
                type="text"
                value={userInput}
                onChange={handleUserInputChange}
                placeholder="输入你的行动... (例如: 前往客厅, 和林若曦说话：你好)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !userInput.trim()}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? '处理中...' : '执行'}
              </button>
            </form>
            <p className="text-xs text-gray-500 mt-2">
              💡 提示: 你可以移动到其他房间、与角色对话、或进行其他行动
            </p>
          </div>
        </div>
      </div>

      {/* NPC对话模态窗口 */}
      {showDialogueModal && currentNpcDialogue && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[80vh] flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">与 {currentNpcDialogue.name} 对话</h3>
              <button
                onClick={() => setShowDialogueModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            {/* 对话历史 */}
            <div className="flex-1 overflow-y-auto mb-4 border rounded p-3 bg-gray-50 max-h-60">
              {npcDialogueHistory.length > 0 ? (
                npcDialogueHistory.map((entry, index) => (
                  <div key={index} className="mb-2 text-sm">
                    <strong>{entry.speaker === "玩家" ? "你" : entry.speaker}:</strong> {entry.message}
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-sm">还没有对话记录</p>
              )}
            </div>

            {/* 输入框 */}
            <form onSubmit={handleNpcChatSubmit} className="flex space-x-2">
              <input
                type="text"
                value={npcChatInput}
                onChange={handleNpcChatInputChange}
                placeholder="输入你想说的话..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={!npcChatInput.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
              >
                发送
              </button>
            </form>
          </div>
        </div>
      )}

      {/* 调试控制台模态窗口 */}
      {showConsole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[80vh] flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">调试控制台</h3>
              <div className="flex space-x-2">
                <button
                  onClick={fetchConsoleData}
                  disabled={consoleLoading}
                  className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 disabled:bg-gray-400"
                >
                  {consoleLoading ? '刷新中...' : '刷新'}
                </button>
                <button
                  onClick={() => setShowConsole(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto">
              {consoleData ? (
                <div className="space-y-4">
                  <div className="text-sm text-gray-500">
                    最后更新: {consoleData.timestamp}
                  </div>
                  
                  {consoleData.error ? (
                    <div className="text-red-600 font-mono text-sm">
                      错误: {consoleData.error}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">游戏状态</h4>
                        <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
                          {JSON.stringify(consoleData.gameState, null, 2)}
                        </pre>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">NPC状态</h4>
                        <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
                          {JSON.stringify(consoleData.npcStatus, null, 2)}
                        </pre>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-2">位置状态</h4>
                        <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
                          {JSON.stringify(consoleData.locationStatus, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-gray-500">
                  {consoleLoading ? '正在加载调试信息...' : '点击刷新获取调试信息'}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 新建故事模态窗口 */}
      <NewStoryModal 
        isOpen={showNewStoryModal} 
        onClose={() => setShowNewStoryModal(false)} 
      />
    </div>
  );
} 