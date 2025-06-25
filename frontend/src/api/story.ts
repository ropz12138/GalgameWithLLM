import { createApiRequest } from './index';

// 故事类型定义
export interface Story {
  id: number;
  name: string;
  description: string;
  creator_id: number;
  creator_username?: string; // 创建者用户名（可选）
  game_config: GameConfig;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

// 位置类型定义
export interface Location {
  id?: number;
  story_id?: number;
  key: string;
  name: string;
  en_name: string;
  description: string;
  connections: string[];
  created_at?: string;
  updated_at?: string;
}

// NPC类型定义
export interface NPC {
  id?: number;
  story_id?: number;
  name: string;
  personality: string;
  background: string;
  mood: string;
  relations: Record<string, any>;
  schedule: ScheduleItem[];
  created_at?: string;
  updated_at?: string;
}

// 日程项类型定义
export interface ScheduleItem {
  start_time: string;
  end_time: string;
  location: string;
  event: string;
}

// 游戏配置类型定义
export interface GameConfig {
  user_name: string;
  user_place: string;
  init_time: string;
}

// 创建故事请求参数
export interface CreateStoryRequest {
  name: string;
  description?: string;
  game_config?: GameConfig;
}

// 创建完整故事请求参数
export interface CreateCompleteStoryRequest {
  name: string;
  description?: string;
  npcs: NPC[];
  locations: Location[];
  game_config: GameConfig;
}

// 更新故事请求参数
export interface UpdateStoryRequest {
  name?: string;
  description?: string;
  game_config?: GameConfig;
}

// 保存故事数据请求参数
export interface SaveStoryDataRequest {
  story_id: number;
  npcs: NPC[];
  locations: Location[];
  game_config: GameConfig;
}

// 创建完整故事响应数据
export interface CreateCompleteStoryResponse {
  story: Story;
  locations: Location[];
  npcs: NPC[];
  message: string;
}

// 故事详情响应数据
export interface StoryDetailsResponse {
  id: number;
  name: string;
  description: string;
  creator_id: number;
  game_config: GameConfig;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  locations: Location[];
  npcs: NPC[];
}

// 故事API类
export class StoryApi {
  /**
   * 获取用户的所有故事
   */
  static async getUserStories(token: string): Promise<Story[]> {
    return createApiRequest<Story[]>('/stories/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  /**
   * 获取故事详情
   */
  static async getStoryDetails(storyId: number, token: string): Promise<StoryDetailsResponse> {
    return createApiRequest<StoryDetailsResponse>(`/stories/${storyId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  /**
   * 创建基础故事
   */
  static async createStory(storyData: CreateStoryRequest, token: string): Promise<Story> {
    return createApiRequest<Story>('/stories/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(storyData),
    });
  }

  /**
   * 创建完整故事（包含NPC和位置）
   */
  static async createCompleteStory(storyData: CreateCompleteStoryRequest, token: string): Promise<CreateCompleteStoryResponse> {
    console.log('🚀 [StoryApi] 开始创建完整故事请求');
    console.log('📝 [StoryApi] 故事信息:', {
      name: storyData.name,
      description: storyData.description?.substring(0, 100) + (storyData.description && storyData.description.length > 100 ? '...' : ''),
      npcCount: storyData.npcs.length,
      locationCount: storyData.locations.length,
      gameConfig: storyData.game_config
    });
    
    // 验证token
    if (!token || token.trim() === '') {
      console.error('❌ [StoryApi] Token验证失败 - Token为空');
      throw new Error('认证失败：缺少访问令牌');
    }
    
    // 记录token信息（不记录完整token）
    const tokenPreview = token.length > 20 ? `${token.substring(0, 10)}...${token.substring(token.length - 10)}` : '***';
    console.log('🔑 [StoryApi] Token预览:', tokenPreview);
    
    try {
      const response = await createApiRequest<CreateCompleteStoryResponse>('/stories/create-complete', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(storyData),
      });
      
      console.log('✅ [StoryApi] 故事创建成功:', {
        storyId: response.story?.id,
        storyName: response.story?.name,
        locationCount: response.locations?.length || 0,
        npcCount: response.npcs?.length || 0,
        message: response.message
      });
      
      return response;
      
    } catch (error: any) {
      console.error('❌ [StoryApi] 创建完整故事失败:', error);
      
      // 根据错误类型提供更详细的错误信息
      if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        console.error('🔐 [StoryApi] 认证错误 - Token可能已过期或无效');
        throw new Error('认证失败：请重新登录');
      } else if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
        console.error('🚫 [StoryApi] 权限错误 - 用户没有创建故事的权限');
        throw new Error('权限不足：无法创建故事');
      } else if (error.message?.includes('400') || error.message?.includes('Bad Request')) {
        console.error('📝 [StoryApi] 请求数据错误');
        throw new Error('请求数据有误：' + (error.message || '请检查输入的故事信息'));
      } else if (error.message?.includes('500') || error.message?.includes('Internal Server Error')) {
        console.error('🔧 [StoryApi] 服务器内部错误');
        throw new Error('服务器错误：请稍后重试');
      } else if (error.name === 'NetworkError' || error.message?.includes('fetch')) {
        console.error('🌐 [StoryApi] 网络连接错误');
        throw new Error('网络连接失败：请检查网络连接');
      } else {
        console.error('❓ [StoryApi] 未知错误:', error);
        throw new Error('创建故事失败：' + (error.message || '未知错误'));
      }
    }
  }

  /**
   * 更新故事信息
   */
  static async updateStory(storyId: number, storyData: UpdateStoryRequest, token: string): Promise<Story> {
    return createApiRequest<Story>(`/stories/${storyId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(storyData),
    });
  }

  /**
   * 删除故事
   */
  static async deleteStory(storyId: number, token: string): Promise<{ message: string }> {
    return createApiRequest<{ message: string }>(`/stories/${storyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  /**
   * 保存故事数据
   */
  static async saveStoryData(storyData: SaveStoryDataRequest, token: string): Promise<{ message: string; locations: Location[]; npcs: NPC[] }> {
    return createApiRequest<{ message: string; locations: Location[]; npcs: NPC[] }>('/stories/save-data', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(storyData),
    });
  }

  /**
   * 获取故事信息（用于编辑器）
   */
  static async getStoryInfo(): Promise<{
    npcs: NPC[];
    locations: Location[];
    game_config: GameConfig;
  }> {
    return createApiRequest<{
      npcs: NPC[];
      locations: Location[];
      game_config: GameConfig;
    }>('/story/info', {
      method: 'GET',
    });
  }

  /**
   * 获取当前用户的所有故事（需要认证）
   */
  static async getAllStories(token: string): Promise<Story[]> {
    console.log('🚀 [StoryApi] 开始获取用户故事请求（需要认证）');
    
    // 验证token
    if (!token || token.trim() === '') {
      console.error('❌ [StoryApi] Token验证失败 - Token为空');
      throw new Error('认证失败：缺少访问令牌');
    }
    
    try {
      const response = await createApiRequest<Story[]>('/stories/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      console.log('✅ [StoryApi] 获取用户故事成功:', {
        storyCount: response.length,
        stories: response.map(story => ({
          id: story.id,
          name: story.name,
          creator: story.creator_username || 'Unknown',
          createdAt: story.created_at
        }))
      });
      
      return response;
      
    } catch (error: any) {
      console.error('❌ [StoryApi] 获取用户故事失败:', error);
      
      // 根据错误类型提供更详细的错误信息
      if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        console.error('🔐 [StoryApi] 认证错误 - Token可能已过期或无效');
        throw new Error('认证失败：请重新登录');
      } else if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
        console.error('🚫 [StoryApi] 权限错误');
        throw new Error('权限不足：无法访问此资源');
      } else if (error.message?.includes('500') || error.message?.includes('Internal Server Error')) {
        console.error('🔧 [StoryApi] 服务器内部错误');
        throw new Error('服务器错误：请稍后重试');
      } else if (error.name === 'NetworkError' || error.message?.includes('fetch')) {
        console.error('🌐 [StoryApi] 网络连接错误');
        throw new Error('网络连接失败：请检查网络连接');
      } else {
        console.error('❓ [StoryApi] 未知错误:', error);
        throw new Error('获取故事列表失败：' + (error.message || '未知错误'));
      }
    }
  }
} 