import React, { useState, useEffect, FormEvent, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { NewStoryModal } from './NewStoryModal';
import { StoryApi, Story } from '../api/story';
import { GameApi, GameMessage, MessageHistoryResponse } from '../api/game';
import { API_BASE_URL } from '../api';

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

// API基础配置已在api层统一管理

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

  // 新增：故事列表相关状态
  const [allStories, setAllStories] = useState<Story[]>([]);
  const [storiesLoading, setStoriesLoading] = useState(false);
  const [storiesError, setStoriesError] = useState<string | null>(null);
  const [showStoriesList, setShowStoriesList] = useState(false);

  // 新建故事弹窗状态
  const [showNewStoryModal, setShowNewStoryModal] = useState(false);

  // 新增状态：消息历史
  const [messageHistory, setMessageHistory] = useState<GameMessage[]>([]);
  const [selectedStoryId, setSelectedStoryId] = useState<number | null>(null);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [messagesError, setMessagesError] = useState<string | null>(null);

  // 新增状态：待合并的历史消息
  const [pendingHistoryDialogues, setPendingHistoryDialogues] = useState<DialogueEntry[]>([]);
  
  // 使用 useRef 来跟踪是否正在合并，避免重复合并
  const isMergingRef = useRef(false);

  // 新增：侧边栏宽度控制
  const [sidebarWidth, setSidebarWidth] = useState(280); // 默认280px，比原来的1/3更小
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);

  // 侧边栏拖拽调整宽度的处理函数
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      const newWidth = e.clientX;
      // 限制侧边栏宽度在200px到600px之间
      if (newWidth >= 200 && newWidth <= 600) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.body.classList.remove('resizing');
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.classList.add('resizing');
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.classList.remove('resizing');
    };
  }, [isResizing]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // 获取所有故事列表
  const fetchAllStories = async () => {
    console.log('🚀 [GamePage] 开始获取当前用户的故事');
    setStoriesLoading(true);
    setStoriesError(null);

    try {
      // 获取用户token
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('未找到认证令牌，请重新登录');
      }

      const stories = await StoryApi.getAllStories(token);
      setAllStories(stories);
      console.log('✅ [GamePage] 获取故事成功:', stories);
    } catch (e: any) {
      console.error('❌ [GamePage] 获取故事失败:', e);
      setStoriesError(e.message || '获取故事列表失败');
      
      // 如果是认证错误，跳转到登录页
      if (e.message?.includes('认证失败') || e.message?.includes('请重新登录')) {
        logout();
        navigate('/login');
      }
    } finally {
      setStoriesLoading(false);
    }
  };

  // 将GameMessage转换为DialogueEntry的函数
  const convertGameMessageToDialogue = (message: GameMessage): DialogueEntry[] => {
    const entries: DialogueEntry[] = [];
    
    switch (message.message_type_name) {
      case 'user_input':
        entries.push({
          speaker: '玩家',
          message: message.content
        });
        break;
        
      case 'npc_dialogue':
        entries.push({
          speaker: message.related_entity_name || 'NPC',
          message: message.content
        });
        break;
        
      case 'system_action':
        entries.push({
          speaker: '系统',
          message: message.content
        });
        break;
        
      case 'sensory_feedback':
        entries.push({
          speaker: '系统',
          message: message.content
        });
        break;
        
      case 'system_info':
        entries.push({
          speaker: '系统',
          message: message.content
        });
        break;
        
      case 'error_message':
        entries.push({
          speaker: '系统',
          message: `❌ ${message.content}`
        });
        break;
        
      default:
        entries.push({
          speaker: '系统',
          message: message.content
        });
    }
    
    return entries;
  };

  // 处理故事按钮点击 - 修改以加载消息历史到主聊天框
  const handleStoryButtonClick = async (story: Story) => {
    console.log('🎮 [GamePage] 选择故事:', story);
    
    // 清空相关状态，避免旧数据干扰
    setMessagesError(null);
    setPendingHistoryDialogues([]);
    setMessageHistory([]);
    
    // 先设置故事ID，触发useEffect重新获取游戏状态
    setSelectedStoryId(story.id);
    
    // 获取用户token
    const token = localStorage.getItem('token');
    if (!token) {
      setMessagesError('未找到认证令牌，请重新登录');
      return;
    }
    
    // 加载故事的消息历史
    setMessagesLoading(true);
    setMessagesError(null);
    
    try {
      console.log('📚 [GamePage] 开始加载故事消息历史...');
      const messagesResponse = await GameApi.getStoryMessages({
        storyId: story.id,
        sessionId: undefined, // 获取所有会话的消息
        limit: 100,
        offset: 0
      }, token);
      
      setMessageHistory(messagesResponse.messages);
      console.log('✅ [GamePage] 消息历史加载成功:', {
        count: messagesResponse.messages.length,
        totalCount: messagesResponse.total_count
      });
      
      // 如果有历史消息，将其转换为对话格式
      if (messagesResponse.messages.length > 0) {
        const historyDialogues: DialogueEntry[] = [];
        messagesResponse.messages.forEach(message => {
          const dialogues = convertGameMessageToDialogue(message);
          historyDialogues.push(...dialogues);
        });
        
        console.log('✅ [GamePage] 历史消息已准备好:', historyDialogues.length);
        
        // 使用一个状态来存储待合并的历史消息
        // 当游戏状态更新后，这些消息会被合并进去
        setPendingHistoryDialogues(historyDialogues);
      } else {
        setPendingHistoryDialogues([]);
        console.log('📚 [GamePage] 这是一个空故事，没有历史消息');
      }
      
    } catch (e: any) {
      console.error('❌ [GamePage] 加载故事消息历史失败:', e);
      setMessagesError(e.message || '加载消息历史失败');
      
      // 如果是认证错误，跳转到登录页
      if (e.message?.includes('认证失败') || e.message?.includes('请重新登录')) {
        logout();
        navigate('/login');
      }
    } finally {
      setMessagesLoading(false);
    }
  };

  // 切换故事列表显示状态
  const toggleStoriesList = () => {
    setShowStoriesList(!showStoriesList);
    if (!showStoriesList && allStories.length === 0) {
      fetchAllStories();
    }
  };

  // Fetch initial game state
  useEffect(() => {
    const fetchGameState = async () => {
      // 如果没有选择故事，清空游戏状态
      if (!selectedStoryId) {
        console.log("🔍 [前端DEBUG] 没有选择故事，清空游戏状态");
        setGameState(null);
        setIsLoading(false);
        return;
      }

      try {
        console.log("🔍 [前端DEBUG] 开始获取游戏状态");
        console.log("📚 [前端DEBUG] 当前选择的故事ID:", selectedStoryId);
        setIsLoading(true);
        
        // 构建查询参数
        const params = new URLSearchParams();
        params.append('story_id', selectedStoryId.toString());
        const queryString = params.toString();
        const endpoint = `${API_BASE_URL}/game_state?${queryString}`;
        
        console.log("🔍 [前端DEBUG] 请求URL:", endpoint);
        const response = await fetch(endpoint);
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
  }, [selectedStoryId]); // 添加 selectedStoryId 依赖

  // 监听游戏状态和待合并历史消息的变化
  useEffect(() => {
    if (gameState && pendingHistoryDialogues.length > 0 && !isMergingRef.current) {
      console.log('🔄 [GamePage] 合并历史消息到游戏状态');
      console.log('  📊 当前游戏状态对话历史长度:', gameState.dialogue_history.length);
      console.log('  📚 待合并历史消息长度:', pendingHistoryDialogues.length);
      
      // 设置合并标志，防止重复合并
      isMergingRef.current = true;
      
      // 检查是否已经合并过这些消息（简单的重复检查）
      const firstPendingMessage = pendingHistoryDialogues[0];
      const alreadyMerged = gameState.dialogue_history.some(entry => 
        entry.speaker === firstPendingMessage.speaker && 
        entry.message === firstPendingMessage.message
      );
      
      if (!alreadyMerged) {
        // 合并历史消息和当前对话历史
        setGameState(prevState => ({
          ...prevState!,
          dialogue_history: [...pendingHistoryDialogues, ...prevState!.dialogue_history]
        }));
        console.log('✅ [GamePage] 历史消息合并完成');
      } else {
        console.log('⚠️ [GamePage] 发现重复消息，跳过合并');
      }
      
      // 清空待合并的历史消息
      setPendingHistoryDialogues([]);
      
      // 重置合并标志
      setTimeout(() => {
        isMergingRef.current = false;
      }, 100);
    }
  }, [gameState, pendingHistoryDialogues]);

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
        body: JSON.stringify({ 
          action: currentAction,
          story_id: selectedStoryId || 2  // 使用选择的故事ID，默认为2
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const updatedGameState = await response.json();
      console.log(`✅ [前端] API响应成功:`);
      console.log(`  📊 更新后的游戏状态:`, updatedGameState);
      console.log(`  💬 更新后对话历史长度: ${updatedGameState.dialogue_history.length}`);
      console.log(`  💬 对话历史内容:`, updatedGameState.dialogue_history);
      
      // 先更新游戏状态（不包括对话历史）
      setGameState(prevState => ({
        ...updatedGameState,
        dialogue_history: prevState?.dialogue_history || [] // 暂时保持现有历史
      }));

      // 然后重新获取完整的消息历史
      if (selectedStoryId) {
        try {
          const token = localStorage.getItem('token');
          if (token) {
            console.log('🔄 [前端] 重新获取完整消息历史...');
            const messagesResponse = await GameApi.getStoryMessages({
              storyId: selectedStoryId,
              sessionId: undefined,
              limit: 100,
              offset: 0
            }, token);
            
            // 转换消息为对话格式
            const fullDialogueHistory: DialogueEntry[] = [];
            messagesResponse.messages.forEach(message => {
              const dialogues = convertGameMessageToDialogue(message);
              fullDialogueHistory.push(...dialogues);
            });
            
            // 更新完整的对话历史
            setGameState(prevState => prevState ? {
              ...prevState,
              dialogue_history: fullDialogueHistory
            } : null);
            
            console.log('✅ [前端] 完整消息历史更新成功:', fullDialogueHistory.length);
          }
        } catch (historyError) {
          console.error('⚠️ [前端] 获取消息历史失败:', historyError);
          // 历史获取失败不影响主流程，使用后端返回的新消息
          setGameState(prevState => prevState ? {
            ...prevState,
            dialogue_history: [...(prevState.dialogue_history || []), ...(updatedGameState.dialogue_history || [])]
          } : null);
        }
      }

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
        body: JSON.stringify({ 
          action: dialogueMessage,
          story_id: selectedStoryId || 2  // 使用选择的故事ID，默认为2
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const updatedGameState = await response.json();
      console.log(`✅ [前端] NPC对话请求成功:`);
      console.log(`  📊 更新后的游戏状态:`, updatedGameState);
      console.log(`  💬 更新后对话历史长度: ${updatedGameState.dialogue_history.length}`);
      console.log(`  💬 对话历史内容:`, updatedGameState.dialogue_history);
      
      // 先更新游戏状态（不包括对话历史）
      setGameState(prevState => ({
        ...updatedGameState,
        dialogue_history: prevState?.dialogue_history || [] // 暂时保持现有历史
      }));

      // 然后重新获取完整的消息历史
      if (selectedStoryId) {
        try {
          const token = localStorage.getItem('token');
          if (token) {
            console.log('🔄 [前端] 重新获取完整消息历史...');
            const messagesResponse = await GameApi.getStoryMessages({
              storyId: selectedStoryId,
              sessionId: undefined,
              limit: 100,
              offset: 0
            }, token);
            
            // 转换消息为对话格式
            const fullDialogueHistory: DialogueEntry[] = [];
            messagesResponse.messages.forEach(message => {
              const dialogues = convertGameMessageToDialogue(message);
              fullDialogueHistory.push(...dialogues);
            });
            
            // 更新完整的对话历史
            setGameState(prevState => {
              const newState = prevState ? {
                ...prevState,
                dialogue_history: fullDialogueHistory
              } : null;
              
              // 同时更新模态窗口中的对话历史
              if (newState && currentNpcDialogue) {
                const npcDialogueEntries = fullDialogueHistory.filter((entry: DialogueEntry) => 
                  entry.speaker === currentNpcDialogue.name || 
                  (entry.speaker === "玩家" && entry.message.includes(`对${currentNpcDialogue.name}说`)) ||
                  (entry.speaker === currentNpcDialogue.name && entry.message.includes("回复"))
                );
                setNpcDialogueHistory(npcDialogueEntries);
              }
              
              return newState;
            });
            
            console.log('✅ [前端] 完整消息历史更新成功:', fullDialogueHistory.length);
          }
        } catch (historyError) {
          console.error('⚠️ [前端] 获取消息历史失败:', historyError);
          // 历史获取失败不影响主流程，使用后端返回的新消息
          setGameState(prevState => prevState ? {
            ...prevState,
            dialogue_history: [...(prevState.dialogue_history || []), ...(updatedGameState.dialogue_history || [])]
          } : null);
        }
      }

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
              {sensoryData.vision ? (
                <div><strong>👁️ 视觉:</strong> {sensoryData.vision}</div>
              ) : (
                <div>点击展开查看详细的五感反馈信息...</div>
              )}
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
      // 使用当前选择的故事ID，默认为1
      const currentStoryId = selectedStoryId || 1;
      
      // 并行获取多个调试信息
      const [gameStateRes, npcStatusRes, locationStatusRes] = await Promise.all([
        fetch(`${API_BASE_URL}/debug/game_state?story_id=${currentStoryId}`),
        fetch(`${API_BASE_URL}/debug/npc_status?story_id=${currentStoryId}`),
        fetch(`${API_BASE_URL}/debug/location_status?story_id=${currentStoryId}`)
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
    <div className="h-screen bg-gray-100 flex flex-col">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b px-6 py-4 flex-shrink-0">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">🎮 LLM文字游戏</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">欢迎，{user?.username}</span>
            <button
              onClick={toggleStoriesList}
              className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
            >
              {showStoriesList ? '隐藏我的故事' : '查看我的故事'}
            </button>
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

      {/* 游戏主体内容 - 使用固定高度和flex布局 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧游戏状态面板 - 固定高度，内容可滚动 */}
        <div 
          ref={sidebarRef}
          className={`bg-white border-r flex-shrink-0 relative flex flex-col ${isResizing ? 'sidebar-resizing' : ''}`}
          style={{ width: `${sidebarWidth}px` }}
        >
          {/* 侧边栏调整拖拽条 */}
          <div
            className="sidebar-resizer"
            onMouseDown={handleMouseDown}
            title="拖拽调整侧边栏宽度"
          />
          
          {/* 侧边栏内容 - 可滚动 */}
          <div className="sidebar-content flex-1 overflow-y-auto p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">游戏状态</h2>
            
            {/* 故事列表区域 */}
            {showStoriesList && (
              <div className="mb-6 border-b pb-4">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-medium text-gray-700">我的故事</h3>
                  <button
                    onClick={fetchAllStories}
                    disabled={storiesLoading}
                    className="px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600 disabled:bg-gray-400"
                  >
                    {storiesLoading ? '刷新中...' : '刷新'}
                  </button>
                </div>
                
                {storiesError && (
                  <div className="mb-3 p-2 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                    ❌ {storiesError}
                  </div>
                )}
                
                {storiesLoading ? (
                  <div className="text-center py-4">
                    <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                    <p className="mt-1 text-sm text-gray-600">加载中...</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {allStories.length === 0 ? (
                      <div className="text-center py-4 text-gray-500 text-sm">
                        📚 暂无故事，点击"新建故事"开始创作
                      </div>
                    ) : (
                      <>
                        <div className="text-xs text-gray-500 mb-2">
                          共 {allStories.length} 个故事
                        </div>
                        {allStories.map((story) => (
                          <div key={story.id} className="border rounded p-2 bg-gray-50">
                            <div className="flex justify-between items-start">
                              <div className="flex-1 min-w-0">
                                <h4 className="font-medium text-sm text-gray-800 truncate">{story.name}</h4>
                                <p className="text-xs text-gray-600 mt-1 line-clamp-2">{story.description || '暂无描述'}</p>
                                <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
                                  <span>👤 {story.creator_username || 'Unknown'}</span>
                                  <span>🆔 {story.id}</span>
                                </div>
                              </div>
                              <button
                                onClick={() => handleStoryButtonClick(story)}
                                className="ml-2 px-2 py-1 bg-purple-500 text-white rounded text-xs hover:bg-purple-600 flex-shrink-0"
                              >
                                选择
                              </button>
                            </div>
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                )}
              </div>
            )}
            
            {/* 游戏信息区域 */}
            {gameState ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-gray-700">当前位置</h3>
                  <p className="text-gray-600">{gameState.player_location}</p>
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
                        {location}
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
            ) : (
              <div className="space-y-4 text-center py-8">
                <div className="text-6xl">🎮</div>
                <div>
                  <h3 className="text-lg font-medium text-gray-700 mb-2">欢迎来到文字冒险游戏！</h3>
                  <p className="text-gray-600 text-sm mb-4">请从左侧故事列表中选择一个故事开始游戏</p>
                  <div className="space-y-2 text-xs text-gray-500">
                    <div className="flex items-center justify-center space-x-2">
                      <span>📚</span>
                      <span>选择现有故事继续冒险</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <span>✨</span>
                      <span>或创建新故事开始全新的旅程</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 右侧对话和输入区域 - 固定高度，聊天记录独立滚动 */}
        <div className="flex-1 flex flex-col bg-white">
          {/* 标题栏 - 固定 */}
          <div className="flex-shrink-0 p-6 pb-4 border-b">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">游戏记录</h2>
              {selectedStoryId && (
                <div className="text-sm text-blue-600">
                  当前故事: ID {selectedStoryId}
                  {messagesLoading && (
                    <div className="inline-flex items-center ml-2">
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-500"></div>
                      <span className="ml-1">加载历史...</span>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {messagesError && (
              <div className="mt-3 p-2 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                ❌ {messagesError}
              </div>
            )}
          </div>

          {/* 对话历史区域 - 独立滚动 */}
          <div className="flex-1 overflow-y-auto p-6 pt-4">
            <div className="space-y-3">
              {gameState && gameState.dialogue_history.length > 0 ? (
                gameState.dialogue_history.map((entry, index) => renderDialogueEntry(entry, index))
              ) : (
                <p className="text-gray-500">
                  {messagesLoading 
                    ? '正在加载故事消息...' 
                    : selectedStoryId 
                      ? '这个故事还没有消息记录，开始你的冒险吧...' 
                      : '开始你的冒险吧...'
                  }
                </p>
              )}
            </div>
          </div>

          {/* 输入区域 - 固定在底部 */}
          <div className="flex-shrink-0 border-t p-6">
            <form onSubmit={handleUserInputSubmit} className="flex space-x-2">
              <input
                type="text"
                value={userInput}
                onChange={handleUserInputChange}
                placeholder={selectedStoryId 
                  ? "输入你的行动... (例如: 前往其他地点, 和角色说话：你好)" 
                  : "请先选择一个故事..."
                }
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading || !selectedStoryId}
              />
              <button
                type="submit"
                disabled={isLoading || !userInput.trim() || !selectedStoryId}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? '处理中...' : '执行'}
              </button>
            </form>
            <p className="text-xs text-gray-500 mt-2">
              {selectedStoryId 
                ? "💡 提示: 你可以移动到其他地点、与角色对话、或进行其他行动"
                : "📚 请先从左侧选择一个故事开始游戏"
              }
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
        onStoryCreated={() => {
          // 故事创建成功后的回调，可以在这里刷新故事列表或其他操作
          console.log('故事创建成功，可以在这里添加后续操作');
        }}
      />
    </div>
  );
} 