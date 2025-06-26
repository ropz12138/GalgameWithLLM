import React, { useState, useEffect } from 'react';
import { StoryApi, CreateCompleteStoryRequest } from '../api/story';
import { API_BASE_URL } from '../api';
import { useAuth } from '../contexts/AuthContext';

interface NPC {
  name: string;
  personality: string;
  background: string;
  mood: string;
  relations: Record<string, any>;
  schedule: any[];
}

interface Location {
  key: string;
  name: string;
  en_name: string;
  description: string;
  connections: string[];
}

interface GameConfig {
  user_name: string;
  user_place: string;
  init_time: string;
}

interface StoryInfo {
  npcs: NPC[];
  locations: Location[];
  game_config: GameConfig;
}

interface NewStoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStoryCreated?: () => void;
}

// API基础配置已在api层统一管理

export function NewStoryModal({ isOpen, onClose, onStoryCreated }: NewStoryModalProps) {
  const { token } = useAuth();
  const [storyInfo, setStoryInfo] = useState<StoryInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'basic' | 'npcs' | 'locations' | 'config'>('basic');
  
  // 新增：故事基本信息状态
  const [storyName, setStoryName] = useState('');
  const [storyDescription, setStoryDescription] = useState('');
  const [creating, setCreating] = useState(false);
  
  // 新关系输入状态
  const [newRelationInputs, setNewRelationInputs] = useState<Record<number, {key: string, value: string}>>({});
  
  // 新建角色和地点的状态
  const [showNewNPCForm, setShowNewNPCForm] = useState(false);
  const [showNewLocationForm, setShowNewLocationForm] = useState(false);

  // 获取故事信息
  useEffect(() => {
    if (isOpen) {
      fetchStoryInfo();
      // 重置表单状态
      setStoryName('');
      setStoryDescription('');
      setActiveTab('basic');
      setError(null);
    }
  }, [isOpen]);

  const fetchStoryInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/story/info`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('🔍 [NewStoryModal] 获取到的故事信息:', data);
      console.log('🔍 [NewStoryModal] 位置信息:', data.locations);
      
      // 检查每个位置的connections字段
      data.locations?.forEach((location: Location, index: number) => {
        console.log(`🔍 [NewStoryModal] 位置 ${index + 1} (${location.name}) 的连接:`, location.connections);
      });
      
      // 检查每个NPC的日程表字段
      data.npcs?.forEach((npc: NPC, index: number) => {
        console.log(`🔍 [NewStoryModal] NPC ${index + 1} (${npc.name}) 的日程表:`, npc.schedule);
        npc.schedule?.forEach((item: any, scheduleIndex: number) => {
          console.log(`  日程项 ${scheduleIndex + 1}:`, item);
        });
      });
      
      setStoryInfo(data);
    } catch (e) {
      console.error('获取故事信息失败:', e);
      setError(e instanceof Error ? e.message : '获取故事信息失败');
    } finally {
      setLoading(false);
    }
  };

  // 创建完整故事
  const handleCreateStory = async () => {
    console.log('🚀 [NewStoryModal] 开始创建故事流程');
    
    if (!storyInfo || !token) {
      const errorMsg = !storyInfo ? '故事信息未加载' : '用户未登录';
      console.error(`❌ [NewStoryModal] 预检查失败 - ${errorMsg}`);
      setError(`缺少必要信息: ${errorMsg}`);
      return;
    }

    if (!storyName.trim()) {
      console.error('❌ [NewStoryModal] 验证失败 - 故事名称为空');
      setError('请输入故事名称');
      return;
    }

    console.log('📊 [NewStoryModal] 故事数据统计:', {
      name: storyName,
      descriptionLength: storyDescription.length,
      npcCount: storyInfo.npcs.length,
      locationCount: storyInfo.locations.length,
      gameConfig: storyInfo.game_config
    });

    // 记录token状态（不记录完整token）
    const tokenPreview = token.length > 20 ? `${token.substring(0, 10)}...${token.substring(token.length - 10)}` : '***';
    console.log('🔑 [NewStoryModal] Token状态:', {
      hasToken: !!token,
      tokenLength: token.length,
      tokenPreview
    });

    try {
      setCreating(true);
      setError(null);
      
      console.log('⏳ [NewStoryModal] 设置创建状态 - 开始创建');

      const createRequest: CreateCompleteStoryRequest = {
        name: storyName.trim(),
        description: storyDescription.trim(),
        npcs: storyInfo.npcs,
        locations: storyInfo.locations,
        game_config: storyInfo.game_config
      };

      console.log('📝 [NewStoryModal] 创建请求构建完成');
      console.log('🚀 [NewStoryModal] 调用API创建故事');

      const result = await StoryApi.createCompleteStory(createRequest, token);

      console.log('✅ [NewStoryModal] 故事创建成功:', {
        storyId: result.story?.id,
        storyName: result.story?.name,
        createdAt: result.story?.created_at,
        message: result.message
      });

      // 调用成功回调
      if (onStoryCreated) {
        console.log('📞 [NewStoryModal] 调用成功回调');
        onStoryCreated();
      }

      // 关闭弹窗
      console.log('🔄 [NewStoryModal] 关闭弹窗');
      onClose();

      // 显示成功消息
      const successMsg = `故事 "${result.story.name}" 创建成功！`;
      console.log('🎉 [NewStoryModal] 显示成功消息:', successMsg);
      alert(successMsg);

    } catch (e: any) {
      console.error('❌ [NewStoryModal] 创建故事失败:', e);
      
      // 详细的错误日志
      console.error('❌ [NewStoryModal] 错误详情:', {
        errorName: e.name,
        errorMessage: e.message,
        errorStack: e.stack,
        storyName: storyName,
        tokenPreview
      });
      
      // 根据错误类型设置用户友好的错误消息
      let userErrorMessage = '';
      if (e.message?.includes('认证失败') || e.message?.includes('Token')) {
        userErrorMessage = '登录状态已过期，请重新登录后再试';
        console.error('🔐 [NewStoryModal] 认证相关错误');
      } else if (e.message?.includes('权限不足')) {
        userErrorMessage = '您没有创建故事的权限';
        console.error('🚫 [NewStoryModal] 权限相关错误');
      } else if (e.message?.includes('网络')) {
        userErrorMessage = '网络连接失败，请检查网络后重试';
        console.error('🌐 [NewStoryModal] 网络相关错误');
      } else if (e.message?.includes('服务器')) {
        userErrorMessage = '服务器暂时不可用，请稍后重试';
        console.error('🔧 [NewStoryModal] 服务器相关错误');
      } else {
        userErrorMessage = e.message || '创建故事失败，请重试';
        console.error('❓ [NewStoryModal] 其他错误');
      }
      
      setError(userErrorMessage);
      
    } finally {
      setCreating(false);
      console.log('🔄 [NewStoryModal] 重置创建状态');
    }
  };

  // 更新NPC信息
  const updateNPC = (index: number, field: keyof NPC, value: any) => {
    if (!storyInfo) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    updatedNPCs[index] = { ...updatedNPCs[index], [field]: value };
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 更新位置信息
  const updateLocation = (index: number, field: keyof Location, value: any) => {
    if (!storyInfo) return;
    
    const updatedLocations = [...storyInfo.locations];
    updatedLocations[index] = { ...updatedLocations[index], [field]: value };
    
    setStoryInfo({
      ...storyInfo,
      locations: updatedLocations
    });
  };

  // 更新游戏配置
  const updateGameConfig = (field: keyof GameConfig, value: string) => {
    if (!storyInfo) return;
    
    setStoryInfo({
      ...storyInfo,
      game_config: {
        ...storyInfo.game_config,
        [field]: value
      }
    });
  };

  // 处理连接位置的编辑 - 添加连接
  const addLocationConnection = (index: number, connectionKey: string) => {
    if (!storyInfo || !connectionKey) return;
    
    const updatedLocations = [...storyInfo.locations];
    const connections = [...(updatedLocations[index].connections || [])];
    
    if (!connections.includes(connectionKey)) {
      connections.push(connectionKey);
      updatedLocations[index] = { ...updatedLocations[index], connections };
      
      setStoryInfo({
        ...storyInfo,
        locations: updatedLocations
      });
    }
  };

  // 删除连接位置
  const removeLocationConnection = (index: number, connectionKey: string) => {
    if (!storyInfo) return;
    
    const updatedLocations = [...storyInfo.locations];
    const connections = updatedLocations[index].connections.filter(conn => conn !== connectionKey);
    updatedLocations[index] = { ...updatedLocations[index], connections };
    
    setStoryInfo({
      ...storyInfo,
      locations: updatedLocations
    });
  };

  // 处理关系的编辑 - 添加新关系
  const addNPCRelation = (index: number, key: string, value: string) => {
    if (!storyInfo || !key.trim()) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    const relations = { ...updatedNPCs[index].relations };
    relations[key.trim()] = value.trim();
    updatedNPCs[index] = { ...updatedNPCs[index], relations };
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 删除关系
  const removeNPCRelation = (index: number, key: string) => {
    if (!storyInfo) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    const relations = { ...updatedNPCs[index].relations };
    delete relations[key];
    updatedNPCs[index] = { ...updatedNPCs[index], relations };
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 更新关系值
  const updateNPCRelationValue = (index: number, key: string, value: string) => {
    if (!storyInfo) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    const relations = { ...updatedNPCs[index].relations };
    relations[key] = value;
    updatedNPCs[index] = { ...updatedNPCs[index], relations };
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 处理日程的编辑 - 添加新日程项
  const addNPCScheduleItem = (index: number) => {
    if (!storyInfo) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    const schedule = [...updatedNPCs[index].schedule];
    schedule.push({
      start_time: "07:00",
      end_time: "08:00",
      location: "",
      event: "新活动"
    });
    updatedNPCs[index] = { ...updatedNPCs[index], schedule };
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 删除日程项
  const removeNPCScheduleItem = (index: number, scheduleIndex: number) => {
    if (!storyInfo) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    const schedule = [...updatedNPCs[index].schedule];
    schedule.splice(scheduleIndex, 1);
    updatedNPCs[index] = { ...updatedNPCs[index], schedule };
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 更新日程项
  const updateNPCScheduleItem = (index: number, scheduleIndex: number, field: string, value: any) => {
    if (!storyInfo) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    const schedule = [...updatedNPCs[index].schedule];
    schedule[scheduleIndex] = { ...schedule[scheduleIndex], [field]: value };
    updatedNPCs[index] = { ...updatedNPCs[index], schedule };
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 新建角色
  const addNewNPC = () => {
    if (!storyInfo) return;
    
    const newNPC: NPC = {
      name: "新角色",
      personality: "待设定",
      background: "待设定",
      mood: "平静",
      relations: {},
      schedule: []
    };
    
    setStoryInfo({
      ...storyInfo,
      npcs: [...storyInfo.npcs, newNPC]
    });
    
    setShowNewNPCForm(false);
  };

  // 删除角色
  const removeNPC = (index: number) => {
    if (!storyInfo) return;
    
    const updatedNPCs = [...storyInfo.npcs];
    updatedNPCs.splice(index, 1);
    
    setStoryInfo({
      ...storyInfo,
      npcs: updatedNPCs
    });
  };

  // 新建地点
  const addNewLocation = () => {
    if (!storyInfo) return;
    
    const newLocation: Location = {
      key: `new_location_${Date.now()}`,
      name: "新地点",
      en_name: `new_location_${Date.now()}`,
      description: "待设定",
      connections: []
    };
    
    setStoryInfo({
      ...storyInfo,
      locations: [...storyInfo.locations, newLocation]
    });
    
    setShowNewLocationForm(false);
  };

  // 删除地点
  const removeLocation = (index: number) => {
    if (!storyInfo) return;
    
    const locationToRemove = storyInfo.locations[index];
    const updatedLocations = [...storyInfo.locations];
    updatedLocations.splice(index, 1);
    
    // 同时从其他地点的连接中移除这个地点
    updatedLocations.forEach(location => {
      location.connections = location.connections.filter(conn => conn !== locationToRemove.key);
    });
    
    setStoryInfo({
      ...storyInfo,
      locations: updatedLocations
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-6xl mx-4 max-h-[90vh] flex flex-col">
        {/* 头部 */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">新建故事</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ✕
          </button>
        </div>

        {/* 标签页导航 */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('basic')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'basic'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            基本信息
          </button>
          <button
            onClick={() => setActiveTab('npcs')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'npcs'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            角色信息 ({storyInfo?.npcs.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('locations')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'locations'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            位置信息 ({storyInfo?.locations.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('config')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'config'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            游戏配置
          </button>
        </div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-2">加载中...</span>
            </div>
          ) : error ? (
            <div className="text-center text-red-500 py-8">
              <p>❌ {error}</p>
              <button
                onClick={fetchStoryInfo}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                重新加载
              </button>
            </div>
          ) : storyInfo ? (
            <>
              {/* 基本信息标签页 */}
              {activeTab === 'basic' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-800">故事基本信息编辑</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">故事名称</label>
                      <input
                        type="text"
                        value={storyName}
                        onChange={(e) => setStoryName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">故事描述</label>
                      <textarea
                        value={storyDescription}
                        onChange={(e) => setStoryDescription(e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* NPC信息标签页 */}
              {activeTab === 'npcs' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-800">角色信息编辑</h3>
                    <button
                      onClick={addNewNPC}
                      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      + 新建角色
                    </button>
                  </div>
                  {storyInfo.npcs.map((npc, index) => (
                    <div key={index} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="font-medium text-gray-700">角色 {index + 1}: {npc.name}</h4>
                        <button
                          onClick={() => removeNPC(index)}
                          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                        >
                          删除角色
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">姓名</label>
                          <input
                            type="text"
                            value={npc.name}
                            onChange={(e) => updateNPC(index, 'name', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">心情</label>
                          <input
                            type="text"
                            value={npc.mood}
                            onChange={(e) => updateNPC(index, 'mood', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">性格</label>
                          <textarea
                            value={npc.personality}
                            onChange={(e) => updateNPC(index, 'personality', e.target.value)}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">背景</label>
                          <textarea
                            value={npc.background}
                            onChange={(e) => updateNPC(index, 'background', e.target.value)}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            人物关系 ({Object.keys(npc.relations || {}).length} 个关系)
                          </label>
                          <div className="border rounded p-3 bg-white">
                            {Object.entries(npc.relations || {}).map(([key, value]) => (
                              <div key={key} className="flex items-center space-x-2 mb-2">
                                <input
                                  type="text"
                                  value={key}
                                  readOnly
                                  className="w-1/3 px-2 py-1 border border-gray-300 rounded bg-gray-50 text-sm"
                                  placeholder="关系名称"
                                />
                                <input
                                  type="text"
                                  value={String(value)}
                                  onChange={(e) => updateNPCRelationValue(index, key, e.target.value)}
                                  className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                                  placeholder="关系描述"
                                />
                                <button
                                  onClick={() => removeNPCRelation(index, key)}
                                  className="px-2 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
                                >
                                  删除
                                </button>
                              </div>
                            ))}
                                                         <div className="flex items-center space-x-2">
                               <input
                                 type="text"
                                 placeholder="关系名称 (如: 角色名)"
                                 value={newRelationInputs[index]?.key || ''}
                                 onChange={(e) => setNewRelationInputs(prev => ({
                                   ...prev,
                                   [index]: { ...(prev[index] || {}), key: e.target.value }
                                 }))}
                                 className="w-1/3 px-2 py-1 border border-gray-300 rounded text-sm"
                               />
                               <input
                                 type="text"
                                 placeholder="关系描述 (如: 室友)"
                                 value={newRelationInputs[index]?.value || ''}
                                 onChange={(e) => setNewRelationInputs(prev => ({
                                   ...prev,
                                   [index]: { ...(prev[index] || {}), value: e.target.value }
                                 }))}
                                 className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                               />
                               <button
                                 onClick={() => {
                                   const inputs = newRelationInputs[index];
                                   if (inputs?.key.trim() && inputs?.value.trim()) {
                                     addNPCRelation(index, inputs.key, inputs.value);
                                     setNewRelationInputs(prev => ({
                                       ...prev,
                                       [index]: { key: '', value: '' }
                                     }));
                                   }
                                 }}
                                 className="px-2 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600"
                               >
                                 添加
                               </button>
                             </div>
                          </div>
                        </div>
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            日程安排 ({(npc.schedule || []).length} 个日程项)
                          </label>
                          <div className="border rounded p-3 bg-white max-h-60 overflow-y-auto">
                                                         {(npc.schedule || []).map((scheduleItem: any, scheduleIndex: number) => (
                               <div key={scheduleIndex} className="border rounded p-3 mb-3 bg-gray-50">
                                 <div className="flex justify-between items-start mb-2">
                                   <h5 className="font-medium text-sm">
                                     日程项 {scheduleIndex + 1} 
                                     <span className="ml-2 text-xs text-gray-500">
                                       ({scheduleItem.start_time || '未设置'} - {scheduleItem.end_time || '未设置'})
                                     </span>
                                   </h5>
                                   <button
                                     onClick={() => removeNPCScheduleItem(index, scheduleIndex)}
                                     className="px-2 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
                                   >
                                     删除
                                   </button>
                                 </div>
                                                                 <div className="grid grid-cols-2 gap-2">
                                   <div>
                                     <label className="block text-xs text-gray-600 mb-1">开始时间</label>
                                     <input
                                       type="time"
                                       value={scheduleItem.start_time || ''}
                                       onChange={(e) => updateNPCScheduleItem(index, scheduleIndex, 'start_time', e.target.value)}
                                       className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                                     />
                                   </div>
                                   <div>
                                     <label className="block text-xs text-gray-600 mb-1">结束时间</label>
                                     <input
                                       type="time"
                                       value={scheduleItem.end_time || ''}
                                       onChange={(e) => updateNPCScheduleItem(index, scheduleIndex, 'end_time', e.target.value)}
                                       className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                                     />
                                   </div>
                                   <div>
                                     <label className="block text-xs text-gray-600 mb-1">位置</label>
                                     <select
                                       value={scheduleItem.location || ''}
                                       onChange={(e) => updateNPCScheduleItem(index, scheduleIndex, 'location', e.target.value)}
                                       className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                                     >
                                       <option value="">选择位置</option>
                                       {storyInfo?.locations.map(loc => (
                                         <option key={loc.key} value={loc.key}>
                                           {loc.name} ({loc.key})
                                         </option>
                                       ))}
                                     </select>
                                   </div>
                                   <div>
                                     <label className="block text-xs text-gray-600 mb-1">活动内容</label>
                                     <input
                                       type="text"
                                       value={scheduleItem.event || ''}
                                       onChange={(e) => updateNPCScheduleItem(index, scheduleIndex, 'event', e.target.value)}
                                       className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                                       placeholder="例如：吃早饭"
                                     />
                                   </div>
                                 </div>
                              </div>
                            ))}
                            <button
                              onClick={() => addNPCScheduleItem(index)}
                              className="w-full px-3 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded hover:border-blue-500 hover:text-blue-600"
                            >
                              + 添加日程项
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 位置信息标签页 */}
              {activeTab === 'locations' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-800">位置信息编辑</h3>
                    <button
                      onClick={addNewLocation}
                      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      + 新建地点
                    </button>
                  </div>
                  {storyInfo.locations.map((location, index) => (
                    <div key={index} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="font-medium text-gray-700">位置 {index + 1}: {location.name}</h4>
                        <button
                          onClick={() => removeLocation(index)}
                          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                        >
                          删除地点
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">键名</label>
                          <input
                            type="text"
                            value={location.key}
                            onChange={(e) => updateLocation(index, 'key', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">中文名称</label>
                          <input
                            type="text"
                            value={location.name}
                            onChange={(e) => updateLocation(index, 'name', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">英文名称</label>
                          <input
                            type="text"
                            value={location.en_name}
                            onChange={(e) => updateLocation(index, 'en_name', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            连接位置 ({(location.connections || []).length} 个连接)
                          </label>
                          <div className="border rounded p-3 bg-white">
                            {/* 已连接的位置 */}
                            {(location.connections || []).map((connectionKey, connIndex) => {
                              const connectedLocation = storyInfo?.locations.find(loc => loc.key === connectionKey);
                              return (
                                <div key={connIndex} className="flex items-center justify-between mb-2 p-2 bg-gray-50 rounded">
                                  <span className="text-sm">
                                    {connectedLocation ? `${connectedLocation.name} (${connectionKey})` : connectionKey}
                                  </span>
                                  <button
                                    onClick={() => removeLocationConnection(index, connectionKey)}
                                    className="px-2 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
                                  >
                                    删除
                                  </button>
                                </div>
                              );
                            })}
                            
                            {/* 添加新连接 */}
                            <div className="flex items-center space-x-2 mt-2">
                              <select
                                className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                                onChange={(e) => {
                                  if (e.target.value) {
                                    addLocationConnection(index, e.target.value);
                                    e.target.value = '';
                                  }
                                }}
                                defaultValue=""
                              >
                                <option value="">选择要连接的位置</option>
                                {storyInfo?.locations
                                  .filter(loc => 
                                    loc.key !== location.key && 
                                    !(location.connections || []).includes(loc.key)
                                  )
                                  .map(loc => (
                                    <option key={loc.key} value={loc.key}>
                                      {loc.name} ({loc.key})
                                    </option>
                                  ))}
                              </select>
                            </div>
                          </div>
                        </div>
                        <div className="md:col-span-2">
                          <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                          <textarea
                            value={location.description}
                            onChange={(e) => updateLocation(index, 'description', e.target.value)}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 游戏配置标签页 */}
              {activeTab === 'config' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-800">游戏配置编辑</h3>
                  <div className="border rounded-lg p-4 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
                        <input
                          type="text"
                          value={storyInfo.game_config.user_name}
                          onChange={(e) => updateGameConfig('user_name', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">初始位置</label>
                        <input
                          type="text"
                          value={storyInfo.game_config.user_place}
                          onChange={(e) => updateGameConfig('user_place', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">初始时间</label>
                        <input
                          type="text"
                          value={storyInfo.game_config.init_time}
                          onChange={(e) => updateGameConfig('init_time', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="格式: 2024-01-15 07:00"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* 底部按钮 */}
        <div className="flex justify-end space-x-4 p-6 border-t">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
          >
            取消
          </button>
          <button
            className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            onClick={handleCreateStory}
            disabled={creating || loading || !storyName.trim()}
          >
            {creating ? '创建中...' : '新建'}
          </button>
        </div>
      </div>
    </div>
  );
} 